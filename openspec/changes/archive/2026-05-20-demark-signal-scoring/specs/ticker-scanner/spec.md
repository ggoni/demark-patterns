## MODIFIED Requirements

### Requirement: Summary Output
The system SHALL display a concise summary table of identified signals, sorted descending by their importance score.

#### Scenario: Display found signals
- **WHEN** the scan finishes and identifies tickers with signals
- **THEN** the system prints a table with columns: Ticker, Price, Support, Resist, Action, Score, sorted by Score in descending order
