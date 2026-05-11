## Context

The CLI already has a `plot_results()` function in `demark/cli.py` and a `run_all()` pipeline in `demark/engine.py`. Both need small, additive changes.

## Goals / Non-Goals

**Goals:**
- Add `calculate_bollinger_bands()` to the engine using pure pandas (rolling mean + std).
- Render BBands on the existing price panel in `plot_results()`.
- Replace the hardcoded `demark_analysis.png` filename with `{TICKER}_{YYMMDD}.png`.

**Non-Goals:**
- Configurable BBand period or std multiplier (defaults: 20, 2).
- Additional chart panels or new CLI flags.

## Decisions

- **BBands in engine**: Keeps all indicator math in one place; uses `pd.Series.rolling(20)` — no new dependencies.
- **Filename via `datetime.now()`**: Simple, no external deps. Format: `strftime('%y%m%d')`.

## Risks / Trade-offs

- **Risk**: BBands are NaN for the first 19 bars; matplotlib handles this gracefully (gaps in line).
- **Mitigation**: No special handling needed; pandas/matplotlib skip NaN by default.
