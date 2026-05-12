## Why

A system audit revealed that the current DeMark engine deviates significantly from the professional business logic defined in `CONTEXT.md`. These deviations include incorrect TDST line calculation (using setup range instead of Bar 1), missing "Price Flip" start conditions, missing "Perfection" requirements, and missing "Countdown Qualification" rules. Aligning the implementation with these rules is essential for providing accurate, professional-grade signals.

## What Changes

- **TDST Correctness**: Update `calculate_tdst()` to use the extreme (High/Low) of **Bar 1** of the setup, as per standard DeMark rules.
- **Price Flip Integration**: Update `calculate_setup()` to strictly require a Price Flip to initiate a new 9-count sequence.
- **Setup Perfection**: Add `is_perfect` flag to setups, requiring `low[8 or 9] <= min(low[6, 7])` for Buy and `high[8 or 9] >= max(high[6, 7])` for Sell.
- **Countdown Qualification**: Implement the "Bar 13 vs Bar 8" close comparison rule for Countdown completion.

## Capabilities

### Modified Capabilities
- `demark-engine`: Updated with strictly compliant TD Sequential/Countdown logic.

## Impact

- `demark/engine.py`: Major logic updates to `calculate_setup`, `calculate_countdown`, and `calculate_tdst`.
- `tests/test_engine.py`: Update tests to reflect stricter compliance rules.
