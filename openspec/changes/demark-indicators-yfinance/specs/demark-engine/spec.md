## ADDED Requirements

### Requirement: TD Setup Calculation
The system SHALL calculate the TD Setup count for both buy and sell scenarios based on 9 consecutive bars.

#### Scenario: Completion of Buy Setup
- **WHEN** the close of the current bar is less than the close 4 bars earlier for 9 consecutive bars
- **THEN** the system SHALL assign a sequential count from 1 to 9 to each bar and signal a completed Buy Setup at bar 9

#### Scenario: Completion of Sell Setup
- **WHEN** the close of the current bar is greater than the close 4 bars earlier for 9 consecutive bars
- **THEN** the system SHALL assign a sequential count from 1 to 9 to each bar and signal a completed Sell Setup at bar 9

### Requirement: TD Intersection Filtering
The system SHALL validate the TD Intersection criteria to ensure trend exhaustion before proceeding to the countdown.

#### Scenario: Buy Setup Intersection Validation
- **WHEN** a Buy Setup reaches bar 8 or 9
- **THEN** the system SHALL verify if the High of bar 8 or 9 is greater than or equal to the Low of any bar from 3 to 7 bars earlier in the setup

### Requirement: TD Countdown Calculation
The system SHALL calculate the 13-bar TD Countdown after a completed Setup and Intersection.

#### Scenario: Completion of Buy Countdown
- **WHEN** the system identifies 13 bars (not necessarily consecutive) where the Close is less than or equal to the Low 2 bars earlier
- **THEN** the system SHALL signal a completed Buy Countdown at bar 13

#### Scenario: Completion of Sell Countdown
- **WHEN** the system identifies 13 bars (not necessarily consecutive) where the Close is greater than or equal to the High 2 bars earlier
- **THEN** the system SHALL signal a completed Sell Countdown at bar 13
