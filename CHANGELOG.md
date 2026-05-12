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
- Aligned README feature and CLI documentation with current engine rules and `--no-save` behavior.

### Fixed
- Fixed TDST mapping and recommendation signal behavior in engine logic.
- Removed unused test imports and restored a clean lint state.

### Test Hardening
- Added recycle threshold boundary coverage for both directions:
  - Exactly 18 extension bars does not recycle.
  - 19 extension bars does recycle.
- Added delayed bar-13 qualification coverage for both directions:
  - First eligible bar can remain at 12.
  - A later eligible bar can complete countdown 13.
- Added CLI persistence coverage for `--no-save` behavior:
  - `--no-save` skips CSV persistence.
  - `--plot --no-save` still renders plotting without writing analysis artifacts.

### Data Artifacts
- Persisted latest analysis outputs for AAPL, CTRA, GOLD, INFY, INTC, NOK, and VIV (CSV/PNG where applicable).
