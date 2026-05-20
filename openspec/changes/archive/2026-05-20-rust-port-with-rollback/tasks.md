## 1. Project Infrastructure Setup

- [x] 1.1 Add `maturin` and `pyo3` dependencies to `pyproject.toml`
- [x] 1.2 Initialize the Rust crate structure in the repository (e.g. `src/lib.rs` and `Cargo.toml`)

## 2. Rust Core Computational Engine

- [x] 2.1 Port TD Setup calculation loops (9-count and perfection) to Rust
- [x] 2.2 Port TD Intersection validation and TD Countdown calculations (13-count and recycle) to Rust
- [x] 2.3 Port TDST support/resistance calculation and Bollinger Bands indicators to Rust
- [x] 2.4 Port Importance Scoring logic (Relative Volume and Yahoo Finance News counts) to Rust

## 3. Python Extension Bridge (PyO3)

- [x] 3.1 Implement the PyO3 wrapper functions in `src/lib.rs` to expose calculations to Python
- [x] 3.2 Add data-type conversion layer to marshal lists/arrays between Python and Rust

## 4. Python Fallback Wrapper Integration

- [x] 4.1 Update `demark/engine.py` to import the compiled Rust extension with automatic fallback logic
- [x] 4.2 Add environment variable check `DEMARK_USE_RUST` to allow manual bypass/rollback to the Python class

## 5. Parity & Performance Verification

- [x] 5.1 Implement a strict mathematical parity test suite in `tests/test_parity.py` comparing Python vs Rust calculations
- [x] 5.2 Verify performance speedup and complete integration testing
