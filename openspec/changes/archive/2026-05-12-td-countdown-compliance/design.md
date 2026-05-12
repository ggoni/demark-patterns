## Context

`DeMarkEngine.calculate_countdown` in `demark/engine.py` currently:

1. Checks `Close[13] ≤ Close[8]` (Buy) instead of `Low[13] ≤ Close[8]` per slide 21.
2. Does not track whether a new same-direction setup starts mid-countdown or whether it extends ≥ 18 bars (the Recycle scenario from slide 41).

The TDST spec text in the archived change has the support/resistance assignments inverted relative to both the implementation and the source PDF — a documentation error with no runtime impact.

## Goals / Non-Goals

**Goals:**
- Replace `Close[13]` with `Low[13]` (Buy) / `High[13]` (Sell) in the countdown qualifier.
- Detect and cancel an active countdown when a new same-direction setup runs ≥ 18 bars (Recycle).
- Expose a `buy_countdown_recycled` / `sell_countdown_recycled` boolean column so callers can mark the reset bar.
- Fix the prose in the archived TDST spec to match reality.

**Non-Goals:**
- 9-13-9 disqualification logic (separate future change).
- Intra-day timeframe support.
- Changing countdown counting rules for bars 1–12.

## Decisions

### D1 — Use `Low[13]` not `Close[13]` for Buy qualifier

**Decision**: Change the Buy qualifier from `close.iloc[i] <= buy_bar8_close` to `low.iloc[i] <= buy_bar8_close`. Symmetrically, Sell changes from `close.iloc[i] >= sell_bar8_close` to `high.iloc[i] >= sell_bar8_close`.

**Rationale**: Slide 21 is explicit — condition 1 is `Low[13] ≤ Close[8]`. The existing outer loop already enforces `Close[i] ≤ Low[i-2]` (condition 2), so the only missing piece is using the bar's low for condition 1.

**Alternative considered**: Keep `Close` and document the deviation. Rejected — the PDF rule is unambiguous and the fix is a single-token change.

### D2 — Track setup bar count beyond 9 for Recycle detection

**Decision**: Continue incrementing a `same_direction_ext_count` variable after bar 9 of a setup. If a new same-direction setup begins while a countdown is active and that new setup accumulates > 18 qualifying closes, set a `recycled` flag, reset the countdown, and start fresh.

**Implementation sketch**:
```
active_buy_countdown = True
buy_ext_count = 0            # bars of new setup that started mid-countdown

on each bar i:
  if new buy setup bar (close[i] < close[i-4]):
    buy_ext_count += 1
    if buy_ext_count > 18:
      → recycle: reset buy_count, buy_bar8_close; mark recycled column
  else:
    buy_ext_count = 0
```

**Rationale**: The Recycle rule (slide 41) says 18 consecutive closes less than close four bars earlier cancels a countdown. Tracking the extension count inside the countdown loop adds one variable and one branch — minimal complexity.

**Alternative considered**: A separate post-processing pass over the DataFrame. Rejected — the single-pass loop already has all necessary state; a second pass would require re-reading state.

### D3 — Expose `buy_countdown_recycled` / `sell_countdown_recycled` columns

**Decision**: Add boolean columns (default `False`) set to `True` on the bar where a recycle fires. This matches the PDF's "R" annotation and lets downstream callers (CLI, plots) surface it.

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| `Low[13]` change shifts which bars qualify, altering existing test assertions | Update affected tests explicitly; add a regression test comparing old vs new output on a controlled series |
| Recycle extension counter must reset when countdown resets at setup=9 | Reset `ext_count` inside the `if setup_count == 9` branch |
| Archived spec correction touches a completed change directory | Edit in-place; the file is documentation, not code — no re-run needed |
