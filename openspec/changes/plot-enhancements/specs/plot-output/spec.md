## ADDED Requirements

### Requirement: Dynamic Plot Filename
The CLI SHALL save plots using the pattern `{TICKER}_{YYMMDD}.png`.

#### Scenario: Filename Format
- **WHEN** `--plot` is used with `--ticker NVDA` on 2026-05-11
- **THEN** the saved file SHALL be `NVDA_260511.png`

### Requirement: Bollinger Bands Rendered on Plot
The price sub-chart SHALL display the three Bollinger Band lines.

#### Scenario: BBands on Chart
- **WHEN** `plot_results()` is called and BBands columns exist
- **THEN** `bb_upper`, `bb_middle`, and `bb_lower` SHALL be drawn as distinct lines on the price panel
