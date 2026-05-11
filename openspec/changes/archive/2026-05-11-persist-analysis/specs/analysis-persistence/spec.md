## ADDED Requirements

### Requirement: CSV Persistence
The CLI SHALL save the complete results DataFrame to a CSV file after every successful analysis run, unless `--no-save` is passed.

### Requirement: Ad-hoc Output Directory
The CLI SHALL create and use a directory named `analysis/` (in the current working directory) for all generated files (CSV and PNG) by default.

#### Scenario: Default folder creation
- **WHEN** the user runs the CLI and the `analysis/` directory does not exist
- **THEN** the CLI SHALL create the `analysis/` directory before saving files

#### Scenario: File placement
- **WHEN** the CLI generates a plot or CSV
- **THEN** it SHALL save the file inside the `analysis/` directory

### Requirement: Consistent Filename Convention
The CSV filename SHALL follow the same pattern as the plot: `{TICKER}_{YYMMDD}.csv`.

#### Scenario: Filename format
- **WHEN** the ticker is `AAPL` and the date is 2026-05-11
- **THEN** the CSV file SHALL be named `AAPL_260511.csv` and stored in `analysis/AAPL_260511.csv`
