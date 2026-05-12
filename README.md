# DeMark Sequential Indicators with yfinance

A robust technical analysis engine that implements Tom DeMark’s Sequential and Countdown indicators using `yfinance` data.

## Features

- **TD Setup**: Identifies 9-count setups using price-flip gating and setup perfection checks.
- **TD Countdown**: Tracks 13-count exhaustion signals following a completed setup.
- **Bar 13 Qualification**: Enforces DeMark-style qualification using Low[13] <= Close[8] for buy countdowns and High[13] >= Close[8] for sell countdowns.
- **Countdown Recycle Tracking**: Flags extended same-direction setup conditions that reset an active countdown after 18 extension bars.
- **TDST Lines**: Calculates support and resistance from setup bar 1, matching TDST conventions.
- **Vectorized Engine**: High-performance calculations using `pandas` and `numpy`.
- **Trading Recommendations**: Multi-factor decision engine integrating:
  - **Exhaustion Signals**: Setup 9 and Countdown 13 completion.
  - **Volatility Filtering**: Overbought/Oversold detection using Bollinger Bands.
  - **Trend Breakouts**: Event-driven alerts for TDST Support/Resistance crossovers.
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
uv run demark --ticker NVDA --interval 1d --period 1y --plot
uv run demark --ticker AAPL --period 1mo --no-save
```

### CLI Arguments

- `--ticker`: The stock ticker symbol (e.g., AAPL, BTC-USD, NVDA).
- `--interval`: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo).
- `--period`: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max).
- `--plot`: Optional flag to generate a `demark_analysis.png` visualization.
- `--no-save`: Optional flag to skip writing CSV and plot artifacts to `analysis/`.

## Project Structure

- `demark/`: Core package.
  - `providers.py`: `yfinance` data fetching and cleaning.
  - `engine.py`: Vectorized DeMark indicator logic.
  - `cli.py`: Command-line interface and plotting.
- `tests/`: Unit and integration tests.
- `openspec/`: Project specifications and task tracking.

## Technical Details

The engine uses a vectorized approach for TD Setup detection, while TD Countdown and TDST calculations use optimized loops for stateful rules such as price-flip starts, perfection checks, countdown recycling, and delayed bar-13 qualification. This keeps the implementation close to DeMark sequencing rules without giving up performance on larger price series.

## License

MIT
