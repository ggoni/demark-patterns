## ADDED Requirements

### Requirement: Countdown Bar 13 Buy Qualification Uses Low
The engine SHALL qualify a Buy Countdown bar 13 using the bar's `Low`, not its `Close`. Specifically, bar 13 completes the Buy Countdown only when `Low[13] ≤ Close[8]` AND `Close[13] ≤ Low[i-2]` (the latter being the standard counting condition already enforced). While bar 13 is not yet qualified, the count SHALL remain at 12 until a qualifying bar appears.

#### Scenario: Bar 13 qualifies via Low
- **WHEN** a Buy Countdown reaches 12 qualifying bars and the next bar has `Close ≤ Low[i-2]` AND `Low ≤ Close[8]`
- **THEN** `buy_countdown_count` SHALL be set to 13 for that bar and the countdown SHALL deactivate

#### Scenario: Bar 13 does not qualify — count waits
- **WHEN** a bar satisfies `Close ≤ Low[i-2]` but its `Low > Close[8]`
- **THEN** `buy_countdown_count` SHALL remain at 12 and the countdown SHALL continue

#### Scenario: Bar 13 eventually qualifies on a later bar
- **WHEN** subsequent bars continue to satisfy `Close ≤ Low[i-2]` and one finally has `Low ≤ Close[8]`
- **THEN** `buy_countdown_count` SHALL be set to 13 on that bar

### Requirement: Countdown Bar 13 Sell Qualification Uses High
The engine SHALL qualify a Sell Countdown bar 13 using the bar's `High`, not its `Close`. Bar 13 completes the Sell Countdown only when `High[13] ≥ Close[8]` AND `Close[13] ≥ High[i-2]`. While bar 13 is not yet qualified, the count SHALL remain at 12.

#### Scenario: Bar 13 qualifies via High
- **WHEN** a Sell Countdown reaches 12 qualifying bars and the next bar has `Close ≥ High[i-2]` AND `High ≥ Close[8]`
- **THEN** `sell_countdown_count` SHALL be set to 13 and the countdown SHALL deactivate

#### Scenario: Bar 13 does not qualify on first eligible bar
- **WHEN** a bar satisfies `Close ≥ High[i-2]` but its `High < Close[8]`
- **THEN** `sell_countdown_count` SHALL remain at 12
