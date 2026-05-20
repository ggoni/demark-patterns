## Why

Too many daily scanned tickers. Hard to prioritize. Scoring every scanned ticker in the watchlist based on Relative Volume (RVOL) and financial news intensity highlights the most important opportunities immediately, regardless of signal type.

## What Changes

- Fetch 20-day volume history to calculate RVOL for each ticker in the scan.
- Fetch news stories in the last 24 hours using `yfinance` to count news intensity for each ticker.
- Calculate an importance score (0 to 10) for every scanned ticker in the list.
- Display score and sort all scanned tickers descending by score in scanner console output and output CSV.

## Capabilities

### New Capabilities
- `ticker-scoring`: Calculates a composite 0-10 importance score for all scanned tickers using Relative Volume (RVOL) and last 24h news count.

### Modified Capabilities
- `ticker-scanner`: Scanner sorts output by combined score descending and includes the scores in both CLI printouts and CSV exports.

## Impact

- `demark/providers.py`: News and volume history fetching.
- `demark/engine.py`: RVOL and news intensity calculations and scoring engine.
- `demark/cli.py`: Display and sort scanner output by importance score.
