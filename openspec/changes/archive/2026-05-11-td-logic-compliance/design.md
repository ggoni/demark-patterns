# Design: TD Logic Compliance

## [MODIFY] [engine.py](file:///Users/ggoni/prototypes/demark-patterns/demark/engine.py)

### `calculate_setup`
- Refactor the loop to track `count` and check for the `price_flip` condition when `count == 0`.
- Add an `is_perfect` column to the DataFrame.
- At `count == 9`, evaluate the Perfection criteria and mark the row.

### `calculate_countdown`
- Store `bar8_close` during the countdown.
- At `count == 13`, verify `Close <= bar8_close` (for Buy).
- If not qualified, don't increment to 13; wait for the next qualifying bar.

### `calculate_tdst`
- Locate the index where `setup_count == 1`.
- Use the `Low` (Support) or `High` (Resistance) of that specific index.
- Propagate this value until the next setup completion.

## Verification Plan

### Automated Tests
- `uv run scratch/audit_logic.py` must now pass (expected values: TDST Support based on Bar 1).
- Update `tests/test_engine.py` with specific edge cases for Bar 13 qualification and Price Flips.
