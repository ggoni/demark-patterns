## ADDED Requirements

### Requirement: Bollinger Bands Calculation
The engine SHALL compute 20-period Bollinger Bands (BBands) for every bar.

#### Scenario: Standard BBands
- **WHEN** `calculate_bollinger_bands()` is called
- **THEN** the DataFrame SHALL contain columns `bb_upper`, `bb_middle`, and `bb_lower`

#### Scenario: BBands included in run_all
- **WHEN** `run_all()` is invoked
- **THEN** BBands SHALL be present in the returned DataFrame without requiring a separate call
