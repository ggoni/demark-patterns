//! demark_rust — High-performance DeMark indicator core.
//! Exposed to Python via PyO3 as `demark._demark_rust`.

use pyo3::prelude::*;

// ─── Task 2.1: TD Setup (9-count + perfection) ───────────────────────────────

/// Compute TD Setup buy/sell counts and perfection flags.
///
/// Args (all parallel Vec<f64> of equal length):
///   close, high, low
///
/// Returns (buy_count, sell_count, buy_perfect, sell_perfect) as four Vec<i32>
/// where 1 = True and 0 = False for the boolean vecs.
#[pyfunction]
fn calculate_setup(
    close: Vec<f64>,
    high: Vec<f64>,
    low: Vec<f64>,
) -> (Vec<i64>, Vec<i64>, Vec<i32>, Vec<i32>) {
    let n = close.len();
    let mut buy_count = vec![0i64; n];
    let mut sell_count = vec![0i64; n];
    let mut buy_perfect = vec![0i32; n];
    let mut sell_perfect = vec![0i32; n];

    let mut b_count: i64 = 0;
    let mut s_count: i64 = 0;

    for i in 5..n {
        // Buy Setup
        if close[i] < close[i - 4] {
            if b_count == 0 {
                if close[i - 1] >= close[i - 5] {
                    // Price flip
                    b_count = 1;
                }
            } else {
                b_count += 1;
            }
        } else {
            b_count = 0;
        }
        buy_count[i] = b_count;
        if b_count == 9 {
            let lo_min = low[i].min(low[i - 1]);
            let prev_min = low[i - 2].min(low[i - 3]);
            if lo_min <= prev_min {
                buy_perfect[i] = 1;
            }
        }

        // Sell Setup
        if close[i] > close[i - 4] {
            if s_count == 0 {
                if close[i - 1] <= close[i - 5] {
                    // Price flip
                    s_count = 1;
                }
            } else {
                s_count += 1;
            }
        } else {
            s_count = 0;
        }
        sell_count[i] = s_count;
        if s_count == 9 {
            let hi_max = high[i].max(high[i - 1]);
            let prev_max = high[i - 2].max(high[i - 3]);
            if hi_max >= prev_max {
                sell_perfect[i] = 1;
            }
        }
    }

    (buy_count, sell_count, buy_perfect, sell_perfect)
}

// ─── Task 2.2: TD Intersection + TD Countdown ────────────────────────────────

/// Validate TD Intersection.
///
/// Returns (buy_intersection, sell_intersection) as Vec<i32> (0/1 booleans).
#[pyfunction]
fn validate_intersection(
    high: Vec<f64>,
    low: Vec<f64>,
    buy_setup_count: Vec<i64>,
    sell_setup_count: Vec<i64>,
) -> (Vec<i32>, Vec<i32>) {
    let n = high.len();
    let mut buy_int = vec![0i32; n];
    let mut sell_int = vec![0i32; n];

    for i in 0..n {
        let bsc = buy_setup_count[i];
        if bsc == 8 || bsc == 9 {
            let setup_start = i as i64 - (bsc - 1);
            if setup_start >= 0 {
                let ss = setup_start as usize;
                let lo_slice_end = (ss + 7).min(n);
                let lo_slice_start = (ss + 2).min(lo_slice_end);
                if lo_slice_start < lo_slice_end {
                    let min_low = low[lo_slice_start..lo_slice_end]
                        .iter()
                        .cloned()
                        .fold(f64::INFINITY, f64::min);
                    if high[i] >= min_low {
                        buy_int[i] = 1;
                    }
                }
            }
        }

        let ssc = sell_setup_count[i];
        if ssc == 8 || ssc == 9 {
            let setup_start = i as i64 - (ssc - 1);
            if setup_start >= 0 {
                let ss = setup_start as usize;
                let hi_slice_end = (ss + 7).min(n);
                let hi_slice_start = (ss + 2).min(hi_slice_end);
                if hi_slice_start < hi_slice_end {
                    let max_high = high[hi_slice_start..hi_slice_end]
                        .iter()
                        .cloned()
                        .fold(f64::NEG_INFINITY, f64::max);
                    if low[i] <= max_high {
                        sell_int[i] = 1;
                    }
                }
            }
        }
    }

    (buy_int, sell_int)
}

/// Compute TD Countdown (13-count with recycle).
///
/// Returns (buy_cd_count, sell_cd_count, buy_recycled, sell_recycled).
#[pyfunction]
fn calculate_countdown(
    close: Vec<f64>,
    high: Vec<f64>,
    low: Vec<f64>,
    buy_setup_count: Vec<i64>,
    sell_setup_count: Vec<i64>,
) -> (Vec<i64>, Vec<i64>, Vec<i32>, Vec<i32>) {
    let n = close.len();
    let mut buy_cd = vec![0i64; n];
    let mut sell_cd = vec![0i64; n];
    let mut buy_recycled = vec![0i32; n];
    let mut sell_recycled = vec![0i32; n];

    let mut active_buy = false;
    let mut buy_count: i64 = 0;
    let mut buy_bar8_close = f64::NAN;
    let mut buy_ext_count: i64 = 0;

    let mut active_sell = false;
    let mut sell_count: i64 = 0;
    let mut sell_bar8_close = f64::NAN;
    let mut sell_ext_count: i64 = 0;

    for i in 0..n {
        // Recycle tracking
        if active_buy && i >= 4 {
            if close[i] < close[i - 4] {
                buy_ext_count += 1;
            } else {
                buy_ext_count = 0;
            }
            if buy_ext_count > 18 {
                buy_recycled[i] = 1;
                active_buy = false;
                buy_count = 0;
                buy_bar8_close = f64::NAN;
                buy_ext_count = 0;
            }
        }

        if active_sell && i >= 4 {
            if close[i] > close[i - 4] {
                sell_ext_count += 1;
            } else {
                sell_ext_count = 0;
            }
            if sell_ext_count > 18 {
                sell_recycled[i] = 1;
                active_sell = false;
                sell_count = 0;
                sell_bar8_close = f64::NAN;
                sell_ext_count = 0;
            }
        }

        // Start countdown on Setup 9
        if buy_setup_count[i] == 9 && !active_buy {
            active_buy = true;
            buy_count = 0;
            buy_ext_count = 0;
        }
        if sell_setup_count[i] == 9 && !active_sell {
            active_sell = true;
            sell_count = 0;
            sell_ext_count = 0;
        }

        // Buy Countdown
        if active_buy && i >= 2 {
            if close[i] <= low[i - 2] {
                if buy_count < 12 {
                    buy_count += 1;
                    if buy_count == 8 {
                        buy_bar8_close = close[i];
                    }
                    buy_cd[i] = buy_count;
                } else if low[i] <= buy_bar8_close {
                    buy_cd[i] = 13;
                    active_buy = false;
                    buy_count = 0;
                }
            }
        }

        // Sell Countdown
        if active_sell && i >= 2 {
            if close[i] >= high[i - 2] {
                if sell_count < 12 {
                    sell_count += 1;
                    if sell_count == 8 {
                        sell_bar8_close = close[i];
                    }
                    sell_cd[i] = sell_count;
                } else if high[i] >= sell_bar8_close {
                    sell_cd[i] = 13;
                    active_sell = false;
                    sell_count = 0;
                }
            }
        }
    }

    (buy_cd, sell_cd, buy_recycled, sell_recycled)
}

// ─── Task 2.3: TDST + Bollinger Bands ─────────────────────────────────────────

/// Compute TDST support/resistance levels.
///
/// Returns (tdst_support, tdst_resistance) as Vec<f64> (NaN where not set).
#[pyfunction]
fn calculate_tdst(
    high: Vec<f64>,
    low: Vec<f64>,
    buy_setup_count: Vec<i64>,
    sell_setup_count: Vec<i64>,
) -> (Vec<f64>, Vec<f64>) {
    let n = high.len();
    let mut support = vec![f64::NAN; n];
    let mut resistance = vec![f64::NAN; n];

    let mut last_support = f64::NAN;
    let mut last_resistance = f64::NAN;
    let mut pending_resistance = f64::NAN;
    let mut pending_support = f64::NAN;

    for i in 0..n {
        if buy_setup_count[i] == 1 {
            pending_resistance = high[i];
        }
        if sell_setup_count[i] == 1 {
            pending_support = low[i];
        }
        if buy_setup_count[i] == 9 {
            last_resistance = pending_resistance;
        }
        if sell_setup_count[i] == 9 {
            last_support = pending_support;
        }
        support[i] = last_support;
        resistance[i] = last_resistance;
    }

    (support, resistance)
}

/// Compute Bollinger Bands (SMA ± k*std over a rolling window).
///
/// Returns (bb_middle, bb_upper, bb_lower) as Vec<f64>.
#[pyfunction]
fn calculate_bollinger_bands(close: Vec<f64>, period: usize, std_dev: f64) -> (Vec<f64>, Vec<f64>, Vec<f64>) {
    let n = close.len();
    let mut mid = vec![f64::NAN; n];
    let mut upper = vec![f64::NAN; n];
    let mut lower = vec![f64::NAN; n];

    for i in 0..n {
        if i + 1 >= period {
            let start = i + 1 - period;
            let window = &close[start..=i];
            let mean = window.iter().sum::<f64>() / period as f64;
            // Sample std (ddof=1) to match pandas default
            let variance = window.iter().map(|&x| (x - mean).powi(2)).sum::<f64>()
                / (period as f64 - 1.0);
            let std = variance.sqrt();
            mid[i] = mean;
            upper[i] = mean + std_dev * std;
            lower[i] = mean - std_dev * std;
        }
    }

    (mid, upper, lower)
}

// ─── Task 2.4: Importance Scoring ─────────────────────────────────────────────

/// Compute volume scores for the full series.
///
/// Returns (vol_sma20, rvol, volume_score) as Vec<f64>.
#[pyfunction]
fn calculate_volume_score(volume: Vec<f64>) -> (Vec<f64>, Vec<f64>, Vec<f64>) {
    let n = volume.len();
    let mut vol_sma = vec![f64::NAN; n];
    let mut rvol = vec![0.0f64; n];
    let mut vscore = vec![0.0f64; n];

    for i in 0..n {
        // Rolling 20-period mean with min_periods=1
        let start = if i >= 19 { i - 19 } else { 0 };
        let window = &volume[start..=i];
        let count = window.len() as f64;
        let mean = window.iter().sum::<f64>() / count;
        vol_sma[i] = mean;

        if mean > 0.0 {
            rvol[i] = volume[i] / mean;
        }

        let rv = rvol[i];
        if rv < 1.0 {
            vscore[i] = 5.0 * rv;
        } else {
            vscore[i] = (5.0 + 2.5 * (rv - 1.0)).min(10.0);
        }
    }

    (vol_sma, rvol, vscore)
}

/// Compute news score for a single news_count value.
#[pyfunction]
fn calculate_news_score(news_count: i64) -> f64 {
    if news_count == 0 {
        0.0
    } else if news_count <= 20 {
        0.5 * news_count as f64
    } else {
        10.0
    }
}

// ─── PyO3 Module Registration ─────────────────────────────────────────────────

#[pymodule]
fn _demark_rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(calculate_setup, m)?)?;
    m.add_function(wrap_pyfunction!(validate_intersection, m)?)?;
    m.add_function(wrap_pyfunction!(calculate_countdown, m)?)?;
    m.add_function(wrap_pyfunction!(calculate_tdst, m)?)?;
    m.add_function(wrap_pyfunction!(calculate_bollinger_bands, m)?)?;
    m.add_function(wrap_pyfunction!(calculate_volume_score, m)?)?;
    m.add_function(wrap_pyfunction!(calculate_news_score, m)?)?;
    Ok(())
}
