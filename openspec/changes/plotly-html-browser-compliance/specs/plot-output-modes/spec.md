## ADDED Requirements

### Requirement: Selectable plot output modes
The system SHALL support selectable plot output modes of html, png, and both for analysis plotting workflows.

#### Scenario: HTML-only output mode
- **WHEN** a user selects html output mode
- **THEN** the system SHALL generate HTML artifacts and SHALL NOT generate PNG artifacts.

#### Scenario: PNG-only output mode
- **WHEN** a user selects png output mode
- **THEN** the system SHALL generate PNG artifacts and SHALL NOT generate HTML artifacts.

#### Scenario: Combined output mode
- **WHEN** a user selects both output mode
- **THEN** the system SHALL generate both HTML and PNG artifacts for the same run.

### Requirement: Deterministic artifact naming by mode
The system SHALL use deterministic file naming for HTML and PNG artifacts so outputs are predictable and discoverable.

#### Scenario: Repeat run with same inputs
- **WHEN** the same ticker and date window are analyzed with the same output mode
- **THEN** artifact names SHALL follow the same naming convention for each mode.
