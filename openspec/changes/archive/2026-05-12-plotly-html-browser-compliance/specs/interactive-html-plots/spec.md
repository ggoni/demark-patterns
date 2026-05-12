## ADDED Requirements

### Requirement: Browser-compliant interactive HTML plots
The system SHALL generate Plotly plot artifacts as browser-compliant HTML files that open directly in modern web browsers with interactive controls.

#### Scenario: Generate HTML artifact from analysis run
- **WHEN** a user runs analysis with HTML plot output enabled
- **THEN** the system SHALL write an HTML plot artifact to the analysis output location.

#### Scenario: Open generated artifact in browser
- **WHEN** a generated HTML plot file is opened in a browser
- **THEN** the chart SHALL render with interactive Plotly behavior including zoom and hover.

### Requirement: Portable HTML artifact output
Generated HTML plot artifacts MUST be usable without requiring a running Python process at view time.

#### Scenario: Share artifact across environments
- **WHEN** a user copies the generated HTML file to another machine
- **THEN** the artifact SHALL remain viewable in a supported browser.
