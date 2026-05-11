# DeMark Sequential Indicators with yfinance

A robust technical analysis engine that implements Tom DeMark’s Sequential and Countdown indicators using `yfinance` data.

## Features

- **TD Setup**: Identifies 9-count setups for potential trend reversals.
- **TD Intersection**: Validates setups by checking if the price range of bars 8 or 9 overlaps with the range of bars 3-7.
- **TD Countdown**: Tracks 13-count exhaustion signals following a completed setup.
- **TDST Lines**: Calculates Support (TD Setup Trend) and Resistance levels based on the extremes of completed setups.
- **Vectorized Engine**: High-performance calculations using `pandas` and `numpy`.
- **Interactive CLI**: Fetch data for any ticker and visualize the results.

## Installation

Ensure you have Python 3.11+ and `uv` installed.

```bash
# Install dependencies
uv pip install -r requirements.txt
```

## Usage

Run the analysis for any ticker:

```bash
export PYTHONPATH=$PYTHONPATH:.
python3 demark/cli.py --ticker NVDA --interval 1d --period 1y --plot
```

### CLI Arguments

- `--ticker`: The stock ticker symbol (e.g., AAPL, BTC-USD, NVDA).
- `--interval`: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo).
- `--period`: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max).
- `--plot`: Optional flag to generate a `demark_analysis.png` visualization.

## Project Structure

- `demark/`: Core package.
  - `providers.py`: `yfinance` data fetching and cleaning.
  - `engine.py`: Vectorized DeMark indicator logic.
  - `cli.py`: Command-line interface and plotting.
- `tests/`: Unit and integration tests.
- `openspec/`: Project specifications and task tracking.

## Technical Details

The engine uses a vectorized approach for the TD Setup, while the TD Countdown and TDST lines use optimized loops to handle the state-dependent nature of the 13-count logic. This ensures a balance between performance and accuracy.

## License

MIT
