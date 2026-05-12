# countdown-recycle Specification

## Purpose
TBD - created by archiving change td-countdown-compliance. Update Purpose after archive.
## Requirements
### Requirement: Countdown Recycle on Extended Same-Direction Setup
The engine SHALL detect the Recycle ("R") scenario: when a new same-direction setup begins while a countdown is active and that setup extends beyond 18 consecutive qualifying closes, the active countdown SHALL be cancelled, the engine SHALL mark the cancellation bar with `buy_countdown_recycled = True` (or `sell_countdown_recycled = True`), and a fresh countdown SHALL begin from bar 1 of the next setup completion.

#### Scenario: Recycle fires after 18-bar extension
- **WHEN** a Buy Countdown is active AND a new Buy Setup starts (close < close[i-4]) AND the new setup accumulates more than 18 consecutive qualifying closes without interruption
- **THEN** `buy_countdown_count` SHALL reset to 0 AND `buy_countdown_recycled` SHALL be `True` on the bar where the extension exceeds 18

#### Scenario: New setup under 18 bars does not recycle
- **WHEN** a Buy Countdown is active AND a new Buy Setup begins but is interrupted (count breaks) before reaching 18 bars
- **THEN** the active countdown SHALL continue uninterrupted and `buy_countdown_recycled` SHALL remain `False`

#### Scenario: Recycle resets extension counter
- **WHEN** a recycle fires
- **THEN** the extension counter SHALL reset to 0 so a subsequent new setup must again exceed 18 bars to trigger another recycle

### Requirement: Recycle Columns Initialized
The engine SHALL add `buy_countdown_recycled` and `sell_countdown_recycled` boolean columns to the output DataFrame, defaulting to `False` for all rows.

#### Scenario: Columns present with no recycle events
- **WHEN** `run_all()` is called on a dataset with no recycle-triggering sequences
- **THEN** both recycle columns SHALL exist and all values SHALL be `False`

