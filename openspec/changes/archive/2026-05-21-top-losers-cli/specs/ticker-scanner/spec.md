## ADDED Requirements

### Requirement: Losers Mode CLI Flag
The system SHALL accept `--losers` as a CLI flag that, when present, fetches top N daily losers from Yahoo Finance and runs the scanner on them.

#### Scenario: --losers triggers dynamic scan
- **WHEN** the user runs `uv run demark --losers`
- **THEN** the system fetches the top 10 losers and runs the DeMark scanner on them, printing the signal table to stdout

#### Scenario: --top-n controls count
- **WHEN** the user runs `uv run demark --losers --top-n 5`
- **THEN** the system fetches exactly 5 losers and scans them

#### Scenario: --losers is mutually exclusive with --scan
- **WHEN** the user runs `uv run demark --losers --scan watchlist.txt`
- **THEN** the CLI exits with a non-zero code and prints a usage error

#### Scenario: --losers is mutually exclusive with --ticker
- **WHEN** the user runs `uv run demark --losers --ticker AAPL`
- **THEN** the CLI exits with a non-zero code and prints a usage error

### Requirement: Dynamic Ticker List Input to Scanner
The system SHALL support scanning a ticker list provided programmatically (not only from a file path) without writing a temporary file.

#### Scenario: In-memory ticker list runs full scan
- **WHEN** an internal list of tickers is passed to the scanner pipeline
- **THEN** the system analyzes each ticker, filters for signals, scores them, and outputs the same CSV and stdout table as the file-based scan
