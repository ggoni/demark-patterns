## Why

The CLI today only scans tickers from a static file (`--scan`). There is no way to quickly run DeMark analysis on dynamically fetched market movers. Scanning the top N daily losers from Yahoo Finance lets users identify potential reversal setups (buy setups / buy countdowns) on beaten-down stocks without maintaining a manual watchlist.

## What Changes

- Add `--losers` flag to `demark` CLI that fetches the top N daily losers from Yahoo Finance and runs the existing scanner on them.
- Add `--top-n` integer flag (default: 10) to control how many losers to fetch.
- `--losers` is mutually exclusive with `--scan` and `--ticker`.
- Fetching uses `yfinance` screener or Yahoo Finance market data endpoint -- no external scraping dependency.
- Output is identical to `--scan`: a scored, filtered signal table written to CSV and printed to stdout.

## Capabilities

### New Capabilities

- `losers-source`: Fetch the top N daily loser tickers from Yahoo Finance programmatically and expose them as an input source to the existing scanner pipeline.

### Modified Capabilities

- `ticker-scanner`: Extended to accept a dynamically resolved ticker list (from `losers-source`) in addition to the existing file-based input.

## Impact

- `demark/cli.py`: new `--losers` / `--top-n` args; routing logic to call losers fetch before scanner.
- `demark/providers.py`: new `fetch_losers(n)` method returning a list of ticker strings.
- `tests/test_providers.py`, `tests/test_cli.py`: new tests covering losers fetch and end-to-end losers scan flow.
- No new dependencies if `yfinance` screener API is sufficient; `requests` + HTML parse as fallback.
