## Why

Currently, the DeMark analysis tool processes only one ticker at a time. Traders managing a watchlist need a fast way to scan hundreds of tickers simultaneously and identify those with immediate actionable signals (BUY or SELL) on the latest bar, without manually inspecting each one.

## What Changes

- **New Scanner Mode**: Implement a capability to process a list of tickers from a text file.
- **Signal Filtering**: Add logic to filter analysis results, returning only tickers that exhibit a "BUY" or "SELL" recommendation on the most recent data point.
- **Bulk Processing**: Update the CLI to handle multiple tickers sequentially or in parallel, reading from a file like `line.txt`.
- **Concise Reporting**: Provide a summary view of only the signals found, rather than full historical tables for each ticker.

## Capabilities

### New Capabilities
- `ticker-scanner`: Bulk analysis of tickers from a file with signal-based output filtering.

### Modified Capabilities
<!-- None -->

## Impact

- `demark/cli.py`: Modified to support file-based input and filtered summary output.
- `demark/providers.py`: Used as-is for data fetching.
- `demark/engine.py`: Used as-is for signal calculation.
