# logic-compliance Specification

## Purpose
TBD - created by archiving change td-countdown-compliance. Update Purpose after archive.
## Requirements
### Requirement: TDST Line Definition
The engine SHALL calculate TDST Resistance as the `High` of the **first bar** (count 1) of a completed **Buy Setup** (bearish setup, price declining). The engine SHALL calculate TDST Support as the `Low` of the **first bar** (count 1) of a completed **Sell Setup** (bullish setup, price advancing).

Rationale: During a Buy Setup the market is declining — bar 1 is at the top of the move, so its high becomes the resistance level above. During a Sell Setup the market is advancing — bar 1 is at the bottom of the move, so its low becomes the support level below. This matches the Jason Perl / Christopher Ting presentation (slides 29, 34–37).

#### Scenario: TDST Resistance from Buy Setup Bar 1
- **WHEN** a Buy Setup (9 consecutive closes below close[i-4]) completes
- **THEN** `tdst_resistance` SHALL equal the `High` of the bar where `buy_setup_count == 1`

#### Scenario: TDST Support from Sell Setup Bar 1
- **WHEN** a Sell Setup (9 consecutive closes above close[i-4]) completes
- **THEN** `tdst_support` SHALL equal the `Low` of the bar where `sell_setup_count == 1`

