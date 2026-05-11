## Context

The project aims to provide a standalone Python implementation of the Tom DeMark Sequential indicators. The system will leverage `yfinance` for market data and `pandas` for high-performance indicator calculations.

## Goals / Non-Goals

**Goals:**
- Implement canonical TD Setup (9-count) and TD Countdown (13-count) logic.
- Provide a robust `yfinance` wrapper with data repair capabilities.
- Create a user-friendly CLI for on-demand ticker analysis.
- Ensure high test coverage for the indicator logic using historical known cases.

**Non-Goals:**
- Implementation of TD Combo or other non-Sequential DeMark indicators.
- Real-time data streaming or low-latency websocket integration.
- Automated order execution or brokerage integration.
- Comprehensive GUI or web dashboard (out of scope for this phase).

## Decisions

- **Vectorized Logic**: We will use `pandas` vectorization for the Setup (`Close < Close.shift(4)`) to avoid row-based iteration, ensuring performance even with "max" history datasets.
- **Provider Pattern**: A `MarketDataProvider` abstract class will be implemented to decouple the engine from `yfinance`, allowing for future integrations (e.g., Alpha Vantage, Bloomberg) without rewriting the engine.
- **State Management**: The engine will be stateless, taking a DataFrame as input and returning a DataFrame with added "Setup", "Countdown", and "Signal" columns.
- **CLI Framework**: We will use `argparse` for a lightweight CLI interface.

## Risks / Trade-offs

- **Risk: yFinance Reliability** → Mitigation: Enable `repair=True` in `history()` and implement basic retry logic/validation for returned DataFrames.
- **Risk: Logic Complexity** → Mitigation: Use standard TradingView implementations as a gold standard for unit test comparisons.
- **Trade-off: Speed vs Completeness** → We prioritize the canonical "Sequential" over "Combo" to ensure a robust and verified core before expanding the indicator library.
