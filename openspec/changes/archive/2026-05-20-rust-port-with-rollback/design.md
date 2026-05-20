## Context

The legacy Python `DeMarkEngine` executes sequential computations (recursive TD Setup and TD Countdown) that cannot be vectorized. While fast enough for single-ticker lookups, bulk scanning of hundreds of tickers is bottlenecked by the interpreted Python loops. To resolve this, we will build a high-performance Rust computation backend compiled as a Python extension using `maturin` and `pyo3`. To guarantee 100% rollback safety and preserve the mandatory interactive Plotly HTML visualizers, the Python CLI and plotting layers will remain unchanged, wrapping the Rust computation core with a robust automatic fallback structure.

## Goals / Non-Goals

**Goals:**
- Port the entire calculations (TD Setup, Countdown, Intersection, TDST, Bollinger Bands, and Signal Scores) to a native Rust library.
- Expose the Rust engine to Python as a fast module via `maturin` / `pyo3`.
- Design a dynamic fallback loader that automatically uses the legacy Python implementation if the Rust extension fails to import, load, or run.
- Keep Plotly plotting completely in Python with zero modifications.
- Ensure 100% rollback capability via simple branch checkout or environment variable override.

**Non-Goals:**
- We will NOT rewrite the Python CLI parser or Yahoo Finance HTTP networking library in Rust.
- We will NOT port the Plotly visualizer to Rust.

## Decisions

### 1. Hybrid extension compiled with Maturin & PyO3
- **Rationale**: PyO3 provides seamless bindings between Python objects (e.g. lists and dictionaries) and Rust types. Maturin simplifies building and installing the Rust package as a native Python wheel.
- **Alternative considered**: Writing a pure Rust CLI and porting Plotly. Dismissed because it duplicates networking, command args, and plotting, violating the "preserve plotly" constraint and increasing code size.

### 2. Auto-Fallback Engine Router
- **Rationale**: We will wrap the Rust backend inside a Python class wrapper. At runtime, the class tries to import the Rust extension:
  ```python
  try:
      import _demark_rust as rust_backend
      RUST_AVAILABLE = True
  except ImportError:
      RUST_AVAILABLE = False
  ```
  If `RUST_AVAILABLE` is false or the environment variable `DEMARK_USE_RUST=false` is set, it silently forwards all calls to the Python engine.
- **Alternative considered**: Requiring manual compilation before running the script. Dismissed because it breaks the rollback/safety guarantee.

### 3. Array-based Data Exchange
- **Rationale**: We will pass raw NumPy arrays (like floats) across the PyO3 boundary instead of full Pandas DataFrames. This avoids heavy DataFrame serialization overhead and keeps the memory footprint tiny.

## Risks / Trade-offs

- **[Risk] Compilation failure on target machine** → **Mitigation**: The maturin build is isolated, but if it fails, the router gracefully defaults to the legacy Python code with zero runtime crashes.
- **[Risk] Compilation targets (macOS Apple Silicon/ARM vs Intel)** → **Mitigation**: Maturin automatically detects target architectures and compiles highly optimized native code.
- **[Risk] Math mismatch** → **Mitigation**: Implement parity tests that generate random stock datasets, pass them to both engines, and assert exact float matching down to 6 decimal places.
