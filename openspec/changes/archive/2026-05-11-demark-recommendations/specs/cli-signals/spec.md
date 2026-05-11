## ADDED Requirements

### Requirement: CLI Recommendation Display
The CLI SHALL display the calculated recommendation for each bar in the analysis table.

#### Scenario: Table Action Column
- **WHEN** the analysis table is printed
- **THEN** it SHALL include an "Action" column showing Buy, Sell, or Hold

### Requirement: Latest Signal Summary
The CLI SHALL provide a prominent summary of the latest actionable signal.

#### Scenario: Action Highlight
- **WHEN** the analysis completes
- **THEN** the system SHALL print a clear recommendation message for the most recent bar (e.g., "RECOMENDATION: BUY")
