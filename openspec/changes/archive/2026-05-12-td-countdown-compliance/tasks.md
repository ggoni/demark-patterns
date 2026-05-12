## 1. Bar 13 Qualification Fix

- [x] 1.1 Write a failing test: `test_buy_countdown_bar13_uses_low` — assert that a bar with `Close > Close[8]` but `Low ≤ Close[8]` still completes the countdown
- [x] 1.2 Write a failing test: `test_sell_countdown_bar13_uses_high` — symmetric for sell side
- [x] 1.3 In `calculate_countdown`, change Buy bar 13 check from `close.iloc[i] <= buy_bar8_close` to `low.iloc[i] <= buy_bar8_close`
- [x] 1.4 In `calculate_countdown`, change Sell bar 13 check from `close.iloc[i] >= sell_bar8_close` to `high.iloc[i] >= sell_bar8_close`
- [x] 1.5 Run tests; confirm 1.1 and 1.2 now pass; confirm no existing tests regress

## 2. Recycle Behavior

- [x] 2.1 Write a failing test: `test_buy_countdown_recycle` — build a sequence where a new buy setup exceeds 18 bars mid-countdown; assert `buy_countdown_recycled == True` on the reset bar and `buy_countdown_count` resets
- [x] 2.2 Write a failing test: `test_recycle_columns_always_present` — assert both recycle columns exist and default to `False`
- [x] 2.3 In `calculate_countdown`, initialize `buy_countdown_recycled` and `sell_countdown_recycled` columns to `False`
- [x] 2.4 Add `buy_ext_count = 0` and `sell_ext_count = 0` state variables in the countdown loop
- [x] 2.5 Inside the Buy countdown block: if `close[i] < close[i-4]` (new buy setup bar) increment `buy_ext_count`, else reset to 0; if `buy_ext_count > 18` fire recycle (reset `buy_count`, `buy_bar8_close`, mark column, reset `buy_ext_count`)
- [x] 2.6 Mirror step 2.5 for Sell side
- [x] 2.7 Reset `buy_ext_count` / `sell_ext_count` to 0 whenever a countdown activates (i.e., on `buy_setup_count == 9`)
- [x] 2.8 Run all tests; confirm recycle tests pass; no regression

## 3. TDST Spec Correction

- [x] 3.1 Edit `openspec/changes/archive/2026-05-11-td-logic-compliance/specs/logic-compliance/spec.md` — swap the definitions so "TDST Support = Low of Bar 1 of **Sell** Setup" and "TDST Resistance = High of Bar 1 of **Buy** Setup"
- [x] 3.2 Verify existing `test_tdst_resistance_bar1` and `test_tdst_support_bar1` still pass (no code changed)

## 4. Validation

- [x] 4.1 Run full test suite (`uv run pytest tests/ -q`) — all tests must pass
- [x] 4.2 Run `uv run demark AAPL --csv analysis/AAPL_260511.csv` — spot-check that countdown 13 bars appear on expected dates and no recycle fires on clean data
