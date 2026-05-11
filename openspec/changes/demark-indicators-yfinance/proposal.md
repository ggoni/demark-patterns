## Why

Traders and quantitative analysts require a precise and automated implementation of Tom DeMark's Sequential and Countdown indicators. Using `yfinance` as a source allows for accessible, high-quality market data integration to identify potential trend exhaustion points and market reversals across various asset classes.

## What Changes

- **New DeMark Analysis Engine**: Implementation of the canonical TD Sequential (Setup + Countdown) and TDST lines logic.
- **yFinance Integration**: A dedicated data provider layer to fetch and preprocess OHLCV data from Yahoo Finance.
- **CLI Interface**: A command-line tool to execute DeMark analysis on specific tickers, intervals, and timeframes.
- **Visualization Component**: Simple console-based or basic plotting output to display counts and signals.

## Capabilities

### New Capabilities
- `demark-engine`: Implementation of TD Setup, TD Countdown, TD Intersection, and TDST line logic.
- `market-data-provider`: Integration with `yfinance` for fetching historical and real-time market data.
- `analysis-cli`: Command-line interface for running indicators on user-defined tickers and parameters.

### Modified Capabilities
- None

## Impact

- **New Dependencies**: `yfinance`, `pandas`, `numpy`, and optionally `matplotlib` for visualization.
- **System**: The project will transition from a scaffolded state to a functional technical analysis toolkit.
- **APIs**: No existing APIs are affected; this is a greenfield implementation within the project.
