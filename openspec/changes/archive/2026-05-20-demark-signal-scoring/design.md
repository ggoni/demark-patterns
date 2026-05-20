## Context

DeMark scanners print tickers without a priority hierarchy. Traders need a quick way to rank all tickers in a watchlist or scan list. Integrating Relative Volume (RVOL) and financial news intensity allows ranking and prioritizing all tickers in the list, helping focus on high-priority alerts first.

## Goals / Non-Goals

**Goals:**
- Fetch 20-day volume history to calculate Relative Volume (RVOL = Today Volume / 20-day SMA) for every scanned ticker.
- Fetch news article counts for the last 24 hours from `yfinance` for every scanned ticker.
- Compute a combined 0-10 importance score for all tickers in the scan.
- Sort scanner outputs descending by importance score in CLI and CSV outputs.

**Non-Goals:**
- NLP/Sentiment analysis of the news articles.
- External premium API integrations for sentiment or volume.
- Real-time news streaming or alert notifications.

## Decisions

### News Data Retrieval
- **Choice**: Use the existing `yfinance` ticker `news` endpoint.
- **Alternatives**: Google News API, Alpha Vantage.
- **Rationale**: Direct integration with our existing data library, no additional auth keys required, zero extra cost.

### Scoring Balance
- **Choice**: 60% weight on Relative Volume (RVOL) and 40% weight on News Intensity.
- **Rationale**: Volume represents actual financial commitment (institutional/retail buying pressure), which is a stronger indicator of trend sustainability than media coverage alone.

## Risks / Trade-offs

- **[Risk]** `yfinance` news endpoint rate limits or downtime.
  - **Mitigation** → Wrap news fetching in robust try-except. If it fails, default News Intensity score to 0.0 and proceed without failing the scanner.
- **[Risk]** Extra HTTP requests slow down mass scans as news is fetched for all tickers.
  - **Mitigation** → `yf.Ticker(ticker).news` is lightweight as it is a metadata endpoint. Retrieve it fast, handle any failures quickly, and proceed.
