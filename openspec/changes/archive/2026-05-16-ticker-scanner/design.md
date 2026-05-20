## Context

The current `demark` tool processes individual tickers via the `--ticker` flag. However, identifying trading opportunities requires scanning multiple stocks. The user has a `line.txt` file containing a long, space-separated list of tickers. We need to bridge this gap by adding a scanner mode that automates the analysis for every ticker in a list and surfacing only those with high-probability signals.

## Goals / Non-Goals

**Goals:**
- Add a `--scan <file>` flag to the CLI.
- Read space-separated or line-separated tickers from the provided file.
- Filter results to only show tickers with a `BUY` or `SELL` signal on the most recent bar.
- Provide a summary table output for identified signals.
- Ensure the tool continues scanning even if individual ticker data fetches fail.

**Non-Goals:**
- Multiprocessing/Parallelization: We will stick to sequential processing initially to respect `yfinance` rate limits and keep implementation simple.
- Changing the core `DeMarkEngine` or `YFinanceProvider` logic.

## Decisions

- **Sequential Iteration**: We will iterate through the ticker list sequentially. This provides a predictable execution flow and minimizes the risk of triggering API rate limits.
- **Signal Filter Logic**: Filtering will happen at the CLI/Presentation layer. We will run the full `engine.run_all()` but only print the result if `df.iloc[-1]['recommendation']` starts with "BUY" or "SELL".
- **Graceful Failure**: Each ticker analysis will be wrapped in a `try-except` block. Errors for a specific ticker will be logged to stderr or printed as warnings, ensuring the entire scan doesn't abort.

## Risks / Trade-offs

- [Risk] Performance for extremely large files → [Mitigation] Sequential processing is slower than parallel, but more robust against rate limiting. We will print the ticker being processed to provide feedback to the user.
- [Risk] Ticker validity → [Mitigation] `YFinanceProvider` already handles empty data with a `ValueError`. We will catch this and skip invalid tickers.
