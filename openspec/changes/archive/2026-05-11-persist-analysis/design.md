# Design: Analysis Persistence

## Components

### [MODIFY] [cli.py](file:///Users/ggoni/prototypes/demark-patterns/demark/cli.py)
- **Imports**: Add `os`.
- **Arguments**: Add `--no-save` boolean flag.
- **`plot_results`**:
  - Accept an `output_dir` parameter.
  - Create the directory if it doesn't exist.
  - Save the `.png` file inside the `output_dir`.
- **`save_to_csv` (NEW)**:
  - Takes the `results` DataFrame, `ticker`, and `output_dir`.
  - Generates the filename `{ticker}_{yymmdd}.csv`.
  - Saves the DataFrame using `df.to_csv()`.
- **`main`**:
  - Define `OUTPUT_DIR = "analysis"`.
  - Handle logic for calling `plot_results` and `save_to_csv` based on `--no-save`.

## Logic Flow

1. **Parse CLI**: Get ticker, interval, period, plot, and no-save flags.
2. **Fetch & Calculate**: Same as before.
3. **Display**: Same as before.
4. **Persistence (if not --no-save)**:
   - Identify output directory (default: `analysis`).
   - Create directory if missing (`os.makedirs(..., exist_ok=True)`).
   - Save CSV: `analysis/{TICKER}_{YYMMDD}.csv`.
   - Save Plot (if --plot): `analysis/{TICKER}_{YYMMDD}.png`.
