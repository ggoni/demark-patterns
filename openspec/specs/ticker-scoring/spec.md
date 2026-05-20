# ticker-scoring Specification

## Purpose
TBD - created by archiving change demark-signal-scoring. Update Purpose after archive.
## Requirements
### Requirement: Calculate Relative Volume Score
The system SHALL compute a Relative Volume (RVOL) score from 0 to 10 for each scanned ticker using historical volume data.

#### Scenario: RVOL calculation and scaling below average
- **WHEN** RVOL is less than 1.0 (where RVOL is Today Volume / 20-day Volume SMA)
- **THEN** the system assigns a volume score equal to 5.0 multiplied by RVOL

#### Scenario: RVOL calculation and scaling above average
- **WHEN** RVOL is greater than or equal to 1.0
- **THEN** the system assigns a volume score equal to 5.0 + 2.5 * (RVOL - 1.0), capped at a maximum of 10.0

### Requirement: Calculate News Intensity Score
The system SHALL compute a News Intensity score from 0 to 10 for each scanned ticker using the count of news articles from the last 24 hours.

#### Scenario: News count scaling for zero articles
- **WHEN** the number of articles in the last 24 hours is 0
- **THEN** the system assigns a news score of 0.0

#### Scenario: News count scaling for up to five articles
- **WHEN** the number of articles in the last 24 hours is between 1 and 5 (inclusive)
- **THEN** the system assigns a news score equal to 2.0 multiplied by the number of articles

#### Scenario: News count scaling for more than five articles
- **WHEN** the number of articles in the last 24 hours is greater than 5
- **THEN** the system assigns a news score of 10.0

### Requirement: Calculate Combined Importance Score
The system SHALL compute a combined importance score from 0 to 10 for each scanned ticker in the list using a weighted average of the Relative Volume score and the News Intensity score.

#### Scenario: Combined score weighted calculation
- **WHEN** volume score and news score are calculated for a scanned ticker
- **THEN** the system computes the combined score as (Volume Score * 0.6) + (News Score * 0.4)

