# PR Summary

## What Changed

- Brought TD logic in line with TD Sequential rules:
  - setup price-flip gating and perfection
  - bar-13 qualification uses Low/High vs Close[8]
  - recycle detection and reset behavior
  - TDST mapped from setup bar 1
- Hardened CLI behavior and persistence coverage:
  - `--no-save` skips CSV persistence
  - `--plot --no-save` still renders plot output
  - provider fetch failure path prints error and aborts cleanly
  - direct tests for `save_to_csv` and `plot_results`
- Synced repository docs (`README.md`, `CHANGELOG.md`) with implemented behavior.

## Validation

- `uv run pytest -q` -> 26 passed
- `uv run ruff check .` -> clean
- CLI behavior smoke path validated in prior cycle:
  - `uv run demark --ticker AAPL --period 1mo --no-save`

## Residual Risk

- CLI integration remains primarily mock-driven in tests.
- A non-mocked end-to-end CLI filesystem/plot integration test can further reduce release risk.