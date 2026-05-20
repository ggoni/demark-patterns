## ADDED Requirements

### Requirement: High-Performance Computation Backend
The system SHALL execute TD Setup and TD Countdown calculations using a high-performance Rust extension compiled with `PyO3` / `maturin`.

#### Scenario: Successful computation with Rust engine
- **WHEN** the DeMark analysis is run and the Rust extension is successfully loaded
- **THEN** the calculations return identical indices to the legacy engine in under 1 millisecond

### Requirement: Graceful Rollback Fallback
The system SHALL automatically fall back to the legacy Python `DeMarkEngine` if the Rust engine is uncompiled, raises an exception during calculation, or if the environment variable `DEMARK_USE_RUST=false` is explicitly set.

#### Scenario: Fallback when Rust extension is missing
- **WHEN** the DeMark analysis is run and the compiled Rust binary is not found in the environment
- **THEN** the system falls back to the Python engine class and completes the analysis with zero user-facing errors

#### Scenario: Fallback when user disables Rust engine
- **WHEN** the environment variable `DEMARK_USE_RUST` is set to `false`
- **THEN** the system bypasses the Rust engine entirely and executes calculations via the legacy Python engine

### Requirement: Strict Mathematical Parity
The Rust engine computational outputs for Setup counts, Countdown counts, TDST Support/Resistance levels, Bollinger Bands, and Signal Scores MUST exactly match the Python engine outputs.

#### Scenario: Verification of mathematical parity
- **WHEN** identical historical price and volume dataframes are processed by both the Rust and Python engines
- **THEN** the returned dataframes match perfectly across all computed columns to 6 decimal places
