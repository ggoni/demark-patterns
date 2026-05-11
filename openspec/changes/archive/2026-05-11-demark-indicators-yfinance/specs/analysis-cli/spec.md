## ADDED Requirements

### Requirement: Ticker Analysis Command
The system SHALL provide a CLI command to run DeMark analysis on a specific ticker.

#### Scenario: Running analysis for a ticker
- **WHEN** the user executes the CLI tool with `--ticker AAPL --interval 1d`
- **THEN** the system SHALL fetch the data, calculate counts, and display the latest Setup and Countdown status in the console

### Requirement: Signal Visualization
The system SHALL provide a visual representation of the calculated counts and signals.

#### Scenario: Displaying results in a table
- **WHEN** the analysis is complete
- **THEN** the system SHALL output a formatted table showing the last 15 bars with their corresponding DeMark counts and any active signals
