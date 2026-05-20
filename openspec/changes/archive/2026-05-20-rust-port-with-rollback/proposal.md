## Why

The current Python implementation of Tom DeMark's indicators relies on interpreted sequential loops to compute TD Setup and TD Countdown. These sequential operations cannot be vectorized, resulting in significant execution delay when scanning hundreds of tickers over large historical periods. We need to rebuild the core calculation engine in Rust to achieve high-performance scanning, while ensuring 100% guaranteed rollback to the stable Python implementation and preserving the mandatory interactive Plotly HTML visualizers.

## What Changes

- **BREAKING**: Replaces the default computation backend with a high-performance Rust library compiled using `PyO3` / `maturin`.
- **Core Engine**: Port the DeMark Sequential and Countdown logic, Bollinger Bands, and scoring logic to a Rust module.
- **Rollback Feature**: Introduce a configuration flag (`DEMARK_USE_RUST=true`) or dynamic fallback import. If the Rust module is missing or fails, the tool automatically rolls back to the legacy Python `DeMarkEngine` class with zero user interruption.
- **Verification & Parity**: Establish a strict mathematical parity test suite ensuring the Rust engine outputs identical dataframes as the Python engine.

## Capabilities

### New Capabilities
- `rust-engine`: High-performance Rust computational backend compiled as a Python extension, featuring automated legacy fallback.

### Modified Capabilities
<!-- None -->

## Impact

- **Affected Code**: `demark/engine.py` (updated to support dual-backend routing), `demark/cli.py` (updated to toggle backends).
- **New Dependencies**: `maturin` (build tool), `pyo3` (Rust/Python bindings).
- **APIs**: The interface of `DeMarkEngine` is completely unchanged, ensuring backward compatibility with existing tests and scripts.
