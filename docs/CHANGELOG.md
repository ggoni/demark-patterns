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
- Added clear signal-rule documentation in README, including a Mermaid decision tree.

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
- Added CLI error-path and helper I/O coverage:
  - Provider fetch failure prints error and aborts engine execution.
  - `save_to_csv` writes timestamped CSV output.
  - `plot_results` writes timestamped PNG output.
- Added CLI end-to-end behavior coverage with real engine execution:
  - Persist mode writes CSV/PNG under `analysis/`.
  - `--no-save --plot` writes only PNG in current directory.
- Added CLI setup diagnostics support:
  - New `--debug-setups` flag prints setup-9 counts and latest setup-9 dates.
  - Explicitly explains why TDST support/resistance can remain `NaN` in a selected window.

### Data Artifacts
- Persisted latest analysis outputs for AAPL, CTRA, GOLD, INFY, INTC, NOK, and VIV (CSV/PNG where applicable).
