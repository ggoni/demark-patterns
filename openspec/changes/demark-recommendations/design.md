## Context

The current `DeMarkEngine` calculates raw counts (Setup and Countdown) but does not provide high-level interpretations. Users currently have to look at the table and know that "9" or "13" means a potential reversal.

## Goals / Non-Goals

**Goals:**
- Implement a recommendation layer that interprets engine outputs.
- Update the CLI to display these recommendations clearly.
- Maintain the vectorized nature of the engine where possible.

**Non-Goals:**
- Changing the underlying DeMark logic (counts stay the same).
- Implementing backtesting or performance tracking in this phase.

## Decisions

- **Decision 1: Engine Extension**: I will add a `calculate_recommendations()` method to `DeMarkEngine` rather than creating a separate service. This keeps the logic co-located with the data it interprets.
- **Decision 2: Column Selection**: A new column `recommendation` will be added to the results DataFrame.
- **Decision 3: CLI Formatting**: I will use simple string formatting in the CLI table, and possibly emojis (🔥, 🚀) to highlight Buy/Sell actions.

## Risks / Trade-offs

- **Risk**: Over-simplification of signals (DeMark signals often require context like trend and intersection).
- **Mitigation**: The recommendation will be strictly based on the technical counts, but the full counts will still be visible in the table for user verification.
