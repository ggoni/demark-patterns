## 1. Provider: losers-source

- [x] 1.1 Add `fetch_losers(n: int = 10) -> list[str]` to `YFinanceProvider` using `yf.screen("day_losers")`
- [x] 1.2 Add `fetch_losers` abstract method to `BaseProvider`
- [x] 1.3 Slice result to first `min(n, len(results))` ticker symbols
- [x] 1.4 Raise `RuntimeError` with upgrade hint if `yf.screen` is unavailable or raises

## 2. CLI: flags and routing

- [x] 2.1 Add `--losers` boolean flag and `--top-n` integer flag (default 10) to `argparse`
- [x] 2.2 Put `--losers`, `--scan`, and `--ticker` in a `mutually_exclusive_group`
- [x] 2.3 Add routing: if `args.losers`, call `provider.fetch_losers(args.top_n)` to get ticker list
- [x] 2.4 Refactor: extract `run_scanner_from_list(args, tickers)` shared helper from `run_scanner`
- [x] 2.5 Update `run_scanner` to delegate to `run_scanner_from_list` after reading the file
- [x] 2.6 Wire `--losers` path to call `run_scanner_from_list` with the fetched ticker list

## 3. Tests: provider

- [x] 3.1 Add unit test for `fetch_losers` with mocked `yf.screen` returning sample data
- [x] 3.2 Add unit test for `fetch_losers(n=3)` with more than 3 results (slice assertion)
- [x] 3.3 Add unit test for `fetch_losers` when `yf.screen` raises (expects `RuntimeError`)

## 4. Tests: CLI

- [x] 4.1 Add test that `--losers --scan` raises `argparse` error (mutually exclusive)
- [x] 4.2 Add test that `--losers --ticker AAPL` raises `argparse` error
- [x] 4.3 Add integration test: mock `fetch_losers` returning 2 tickers, assert `run_scanner_from_list` is called with them

## 5. Behavior validation

- [x] 5.1 Run `uv run demark --losers --top-n 3` against live Yahoo Finance and confirm output table appears with up to 3 tickers
- [x] 5.2 Confirm CSV output is written to `analysis/` directory as expected from existing scanner behavior
