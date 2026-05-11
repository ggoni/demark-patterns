## ADDED Requirements

### Requirement: Recommendation Calculation Logic
The system SHALL calculate a recommendation (Buy, Sell, or Hold) for every bar based on DeMark counts.

#### Scenario: Buy Signal from Setup
- **WHEN** the TD Buy Setup count (`buy_setup_count`) is exactly 9
- **THEN** the system SHALL recommend "BUY"

#### Scenario: Buy Signal from Countdown
- **WHEN** the TD Buy Countdown count (`buy_countdown_count`) is exactly 13
- **THEN** the system SHALL recommend "BUY"

#### Scenario: Sell Signal from Setup
- **WHEN** the TD Sell Setup count (`sell_setup_count`) is exactly 9
- **THEN** the system SHALL recommend "SELL"

#### Scenario: Sell Signal from Countdown
- **WHEN** the TD Sell Countdown count (`sell_countdown_count`) is exactly 13
- **THEN** the system SHALL recommend "SELL"

#### Scenario: Default Hold Status
- **WHEN** no Setup or Countdown signals are completed (not 9 or 13)
- **THEN** the system SHALL recommend "HOLD"
