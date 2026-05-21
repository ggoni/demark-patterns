## Context

The `demark` CLI currently accepts ticker input from two sources: `--ticker` (single) and `--scan` (file). The scan pipeline runs `DeMarkEngine` on each ticker and filters for BUY/SELL signals. There is no way to dynamically populate the ticker list from live market data.

`YFinanceProvider` owns all external data access. It already uses `yfinance` for OHLCV data and news. The `yfinance` library exposes `yf.screen()` and the `yf.Screener` API for market screeners, which can return top losers without requiring HTTP scraping.

## Goals / Non-Goals

**Goals:**
- Add `--losers` + `--top-n N` flags to the CLI.
- Implement `YFinanceProvider.fetch_losers(n)` that returns a `list[str]` of ticker symbols.
- Reuse the existing `run_scanner` pipeline without modification.
- Keep zero new hard dependencies (use `yfinance` screener built-ins).

**Non-Goals:**
- Real-time streaming or WebSocket-based data.
- Support for non-US losers (e.g., TSX, LSE).
- Caching or rate-limit management beyond what `yfinance` provides.
- Scraping HTML from Yahoo Finance pages.

## Decisions

### D1: Use `yfinance` screener API, not HTML scraping

`yfinance >= 0.2.54` provides `yf.screen("day_losers")` which returns a ranked list of daily losers as structured data. This is stable, requires no extra dependency, and avoids HTML parsing fragility.

**Alternative considered**: Parse `https://finance.yahoo.com/markets/stocks/losers/` with `requests` + `lxml`. Rejected: brittle against layout changes, adds two dependencies, and violates the project's minimalist stance.

Fallback: if `yf.screen()` is unavailable (older yfinance), raise `RuntimeError` with a clear upgrade message.

### D2: `fetch_losers` lives on `YFinanceProvider`, not in `cli.py`

Keeps data access in the provider layer. The CLI calls `provider.fetch_losers(n)`, then feeds the returned list directly into the existing `run_scanner` path via a synthetic in-memory ticker list (no temp file written).

### D3: `--losers` is mutually exclusive with `--scan` and `--ticker`

Enforced via `argparse` `add_mutually_exclusive_group`. Clear error message if combined.

### D4: Default `--top-n` is 10

Covers a practical scan without overwhelming the user or burning rate limits. User can override up to whatever `yfinance` returns (typically 25-100).

### D5: CLI runner reuse via internal refactor

`run_scanner(args)` currently reads tickers from a file path on `args.scan`. We add a thin adapter: if `args.losers` is set, populate a `tickers` list from `fetch_losers`, then call a shared `run_scanner_from_list(args, tickers)` helper. The existing file-path branch calls the same helper after reading the file. This avoids duplicating scanner logic.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| `yf.screen("day_losers")` API changes or is rate-limited | Catch `Exception`, print actionable error, exit cleanly |
| Fewer than N losers returned by screener | Use `min(n, len(results))` silently; log actual count fetched |
| Old `yfinance` version in user env | Version check at runtime; raise with `pip install --upgrade yfinance` hint |
| Scanner already slow for large N | No change; user controls N; existing per-ticker timeout handling applies |
