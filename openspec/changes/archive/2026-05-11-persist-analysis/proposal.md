## Why

Each CLI run produces a rich analysis (DeMark counts, Bollinger Bands, recommendations) that is currently discarded after display. Persisting the full results DataFrame to disk enables historical tracking, backtesting comparisons, and re-loading prior runs without re-fetching data from yFinance.

## What Changes

- **CSV export per run**: After analysis, the full results DataFrame is saved as `{TICKER}_{YYMMDD}.csv`.
- **Ad-hoc Output Folder**: All generated files (CSV and PNG) will be saved into a dedicated ad-hoc folder (e.g., `analysis/` or similar) created automatically in the current directory to avoid cluttering the root project directory.
- **CLI flag `--no-save`**: Opt-out flag for users who explicitly do not want file output (default: save always).

## Capabilities

### New Capabilities
- `analysis-persistence`: Defines how, when, and where the results DataFrame is saved to disk.
- `output-dir`: Defines the creation and use of an ad-hoc output folder for all generated files.

### Modified Capabilities
None.

## Impact

- `demark/cli.py`: Add file saving logic; create the ad-hoc output folder if it doesn't exist; update `plot_results()` and `main()` to save files there and respect `--no-save`.
- No changes to `demark/engine.py`.
