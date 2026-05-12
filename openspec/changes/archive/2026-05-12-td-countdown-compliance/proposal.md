## Why

The TD Sequential countdown logic deviates from the canonical Jason Perl / Christopher Ting specification in two rule areas: the Bar 13 qualification check uses `Close` instead of `Low` (Buy) / `High` (Sell), and the Recycle ("R") behavior — which cancels an active countdown when a new same-direction setup extends beyond 18 bars — is entirely absent. These gaps produce incorrect signals in real multi-setup sequences, and the existing TDST spec text has its support/resistance definitions inverted, misleading future implementers.

## What Changes

- **Fix Bar 13 countdown qualification**: `Low[13] ≤ Close[8]` for Buy (currently uses `Close[13]`); `High[13] ≥ Close[8]` for Sell (currently uses `Close[13]`).
- **Implement Recycle ("R") behavior**: When a new same-direction setup begins while a countdown is active, and that setup extends beyond 18 consecutive qualifying bars, cancel the active countdown and start fresh (mark the reset bar as "R").
- **Correct TDST spec text**: The existing `specs/logic-compliance/spec.md` has support/resistance definitions swapped — fix the prose to match the correct implementation and the PDF.

## Capabilities

### New Capabilities

- `countdown-bar13-qualification`: Exact two-condition check for countdown completion per slide 21 of the Jason Perl presentation — `Low[13] ≤ Close[8]` (buy) and `High[13] ≥ Close[8]` (sell).
- `countdown-recycle`: Detection and handling of the Recycle ("R") scenario: a new same-direction setup starting mid-countdown that extends ≥ 18 bars resets the countdown.

### Modified Capabilities

- `logic-compliance`: Correct the TDST support/resistance spec prose (swap the definitions to match the implementation and the source PDF).

## Impact

- `demark/engine.py` — `calculate_countdown` method (Bar 13 logic + recycle tracking)
- `openspec/changes/archive/2026-05-11-td-logic-compliance/specs/logic-compliance/spec.md` — prose correction only, no behavior change
- `tests/test_engine.py` — new tests for `Low[13]` condition and recycle scenario
