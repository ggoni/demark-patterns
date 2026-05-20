## ADDED Requirements

### Requirement: File-based Ticker Input
The system SHALL support reading a list of tickers from a text file specified via a CLI flag.

#### Scenario: Read tickers from space-separated file
- **WHEN** the user runs the command with `--scan line.txt` where `line.txt` has space-separated tickers
- **THEN** the system extracts all ticker strings into an internal collection

### Requirement: Signal Filtering
The system SHALL analyze each ticker and filter for "BUY" or "SELL" signals on the most recent bar.

#### Scenario: Include BUY/SELL signals in output
- **WHEN** the analysis engine returns a recommendation of "BUY (Setup Complete)", "SELL (Overbought)", or any other recommendation starting with "BUY" or "SELL" for the latest bar
- **THEN** the system includes that ticker in the results list

#### Scenario: Exclude HOLD signals from output
- **WHEN** the analysis engine returns a recommendation of "HOLD" for the latest bar
- **THEN** the system excludes that ticker from the results list

### Requirement: Summary Output
The system SHALL display a concise summary table of identified signals.

#### Scenario: Display found signals
- **WHEN** the scan finishes and identifies tickers with signals
- **THEN** the system prints a table with columns: Ticker, Price, Support, Resistance, Action

### Requirement: Error Resiliency
The system SHALL skip problematic tickers without aborting the entire scan.

#### Scenario: Handle missing ticker data
- **WHEN** `yfinance` returns no data for a ticker or an error occurs during processing
- **THEN** the system prints a warning message and continues with the next ticker in the list
