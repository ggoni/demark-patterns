# Changelog

All notable changes to this project are documented in this file.

## 2026-05-12

### Added
- Added countdown recycle tracking columns in engine output:
  - buy_countdown_recycled
  - sell_countdown_recycled
- Added OpenSpec published specs:
  - countdown-bar13-qualification
  - countdown-recycle
  - logic-compliance
- Added TD Sequential source presentation to repository for reference.

### Changed
- Updated countdown bar 13 qualification:
  - Buy now uses Low[13] <= Close[8]
  - Sell now uses High[13] >= Close[8]
- Implemented recycle reset behavior for extended same-direction setups.
- Expanded CLI action colorization branches to satisfy lint formatting rules.
- Updated and archived OpenSpec change artifacts for TD logic/countdown compliance.

### Fixed
- Fixed TDST mapping and recommendation signal behavior in engine logic.
- Removed unused test imports and restored a clean lint state.

### Data Artifacts
- Persisted latest analysis outputs for AAPL, CTRA, GOLD, INFY, INTC, NOK, and VIV (CSV/PNG where applicable).
