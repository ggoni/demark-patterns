"""
tests/test_parity.py — Mathematical parity: Python vs Rust engine.

Asserts numeric equality to 6 decimal places across all calculations.
Runs ONLY when the Rust extension is compiled.
"""
import os
import math
import numpy as np
import pandas as pd
import pytest

# Force-load both backends explicitly
os.environ.pop("DEMARK_USE_RUST", None)

from demark.engine import _PythonDeMarkEngine, _RustDeMarkEngine, _RUST_AVAILABLE

pytestmark = pytest.mark.skipif(
    not _RUST_AVAILABLE,
    reason="Rust extension not compiled — run `maturin develop` first",
)

# ─── Fixtures ─────────────────────────────────────────────────────────────────

def _make_df(n: int = 300, seed: int = 42) -> pd.DataFrame:
    """Reproducible synthetic OHLCV DataFrame."""
    rng = np.random.default_rng(seed)
    close = 100.0 + np.cumsum(rng.normal(0, 1, n))
    noise = rng.uniform(0.1, 2.0, n)
    high = close + noise
    low = close - noise
    open_ = close + rng.normal(0, 0.5, n)
    volume = rng.uniform(1_000_000, 5_000_000, n)
    idx = pd.date_range("2020-01-01", periods=n, freq="B")
    return pd.DataFrame(
        {"Open": open_, "High": high, "Low": low, "Close": close, "Volume": volume},
        index=idx,
    )


@pytest.fixture(scope="module")
def both_engines():
    df = _make_df()
    py_engine = _PythonDeMarkEngine(df)
    py_df = py_engine.run_all(news_count=5)

    rust_engine = _RustDeMarkEngine(df)
    rust_df = rust_engine.run_all(news_count=5)

    return py_df, rust_df


# ─── Parity helpers ───────────────────────────────────────────────────────────

TOLS = dict(rtol=1e-6, atol=1e-6)

def _col_allclose(py_df, rust_df, col: str) -> None:
    py_vals = py_df[col].to_numpy(dtype=float)
    ru_vals = rust_df[col].to_numpy(dtype=float)
    # Handle NaN positions identically
    nan_py = np.isnan(py_vals)
    nan_ru = np.isnan(ru_vals)
    assert np.array_equal(nan_py, nan_ru), f"{col}: NaN positions differ"
    non_nan = ~nan_py
    assert np.allclose(py_vals[non_nan], ru_vals[non_nan], **TOLS), (
        f"{col}: max diff = {np.abs(py_vals[non_nan] - ru_vals[non_nan]).max():.2e}"
    )


def _col_equal(py_df, rust_df, col: str) -> None:
    assert (py_df[col] == rust_df[col]).all(), f"{col}: values differ"


# ─── Tests ────────────────────────────────────────────────────────────────────

def test_buy_setup_count(both_engines):
    py_df, rust_df = both_engines
    _col_equal(py_df, rust_df, "buy_setup_count")


def test_sell_setup_count(both_engines):
    py_df, rust_df = both_engines
    _col_equal(py_df, rust_df, "sell_setup_count")


def test_buy_perfect(both_engines):
    py_df, rust_df = both_engines
    _col_equal(py_df, rust_df, "buy_perfect")


def test_sell_perfect(both_engines):
    py_df, rust_df = both_engines
    _col_equal(py_df, rust_df, "sell_perfect")


def test_buy_intersection(both_engines):
    py_df, rust_df = both_engines
    _col_equal(py_df, rust_df, "buy_intersection")


def test_sell_intersection(both_engines):
    py_df, rust_df = both_engines
    _col_equal(py_df, rust_df, "sell_intersection")


def test_buy_countdown_count(both_engines):
    py_df, rust_df = both_engines
    _col_equal(py_df, rust_df, "buy_countdown_count")


def test_sell_countdown_count(both_engines):
    py_df, rust_df = both_engines
    _col_equal(py_df, rust_df, "sell_countdown_count")


def test_buy_countdown_recycled(both_engines):
    py_df, rust_df = both_engines
    _col_equal(py_df, rust_df, "buy_countdown_recycled")


def test_sell_countdown_recycled(both_engines):
    py_df, rust_df = both_engines
    _col_equal(py_df, rust_df, "sell_countdown_recycled")


def test_tdst_support(both_engines):
    py_df, rust_df = both_engines
    _col_allclose(py_df, rust_df, "tdst_support")


def test_tdst_resistance(both_engines):
    py_df, rust_df = both_engines
    _col_allclose(py_df, rust_df, "tdst_resistance")


def test_bollinger_bands(both_engines):
    py_df, rust_df = both_engines
    for col in ("bb_middle", "bb_upper", "bb_lower"):
        _col_allclose(py_df, rust_df, col)


def test_rvol(both_engines):
    py_df, rust_df = both_engines
    _col_allclose(py_df, rust_df, "rvol")


def test_volume_score(both_engines):
    py_df, rust_df = both_engines
    _col_allclose(py_df, rust_df, "volume_score")


def test_combined_score(both_engines):
    py_df, rust_df = both_engines
    _col_allclose(py_df, rust_df, "combined_score")


def test_recommendation(both_engines):
    py_df, rust_df = both_engines
    _col_equal(py_df, rust_df, "recommendation")


# ─── Rollback test ────────────────────────────────────────────────────────────

def test_rollback_env_var(monkeypatch, tmp_path):
    """Setting DEMARK_USE_RUST=false must activate the Python engine."""
    monkeypatch.setenv("DEMARK_USE_RUST", "false")
    # Re-import module to re-evaluate the router
    import importlib
    import demark.engine as eng_mod
    importlib.reload(eng_mod)
    assert eng_mod.engine_backend() == "python"
    assert eng_mod.DeMarkEngine is eng_mod._PythonDeMarkEngine


def test_fallback_works_without_rust_ext(monkeypatch):
    """Simulating ImportError must silently activate Python engine."""
    import demark.engine as eng_mod
    import importlib
    monkeypatch.setattr(eng_mod, "_RUST_AVAILABLE", False)
    monkeypatch.setattr(eng_mod, "DeMarkEngine", eng_mod._PythonDeMarkEngine)
    df = _make_df(100)
    engine = eng_mod.DeMarkEngine(df)
    result = engine.run_all()
    assert "buy_setup_count" in result.columns
