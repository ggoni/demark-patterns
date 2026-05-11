## 1. Engine — Bollinger Bands

- [x] 1.1 Add `calculate_bollinger_bands()` to `DeMarkEngine` (20-period SMA ± 2σ)
- [x] 1.2 Add call to `calculate_bollinger_bands()` inside `run_all()`
- [x] 1.3 Add unit test: verify `bb_upper`, `bb_middle`, `bb_lower` columns exist and bb_upper > bb_lower

## 2. CLI — Plot Enhancements

- [x] 2.1 Update `plot_results()` to draw `bb_upper`, `bb_middle`, `bb_lower` on the price panel
- [x] 2.2 Replace hardcoded `demark_analysis.png` with `{TICKER}_{YYMMDD}.png` filename

## 3. Verification

- [x] 3.1 Run `uv run demark --ticker NVDA --interval 1d --period 1y --plot` and confirm `NVDA_<date>.png` is created with Bollinger Bands visible
