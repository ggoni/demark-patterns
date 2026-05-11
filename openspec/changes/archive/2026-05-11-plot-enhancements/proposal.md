## Why

The current plot (`--plot` flag) saves a generic `demark_analysis.png` that lacks context indicators and a meaningful filename. Adding Bollinger Bands (BBands) provides a widely-used volatility overlay that complements DeMark signals, and a dynamic filename avoids overwriting previous snapshots.

## What Changes

- **Bollinger Bands overlay**: Calculate and render Upper, Middle (SMA-20), and Lower Bollinger Bands on the price chart.
- **Dynamic plot filename**: Save as `{TICKER}_{YYMMDD}.png` (e.g., `NVDA_260511.png`) instead of the hardcoded `demark_analysis.png`.

## Capabilities

### New Capabilities
- `bollinger-bands`: Calculates 20-period SMA and ±2σ Bollinger Bands and adds them to the DataFrame.
- `plot-output`: Defines how the plot file is named and saved.

### Modified Capabilities
None.

## Impact

- `demark/engine.py`: New `calculate_bollinger_bands()` method, called in `run_all()`.
- `demark/cli.py`: `plot_results()` updated to draw BBands and save with the dynamic filename.
