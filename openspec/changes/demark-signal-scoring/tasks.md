## 1. Provider Extensions

- [x] 1.1 Update `YFinanceProvider` in `demark/providers.py` to ensure volume history is fetched and fully populated
- [x] 1.2 Implement a news fetching helper in `demark/providers.py` to retrieve the last 24 hours of news articles count for a ticker

## 2. DeMark Engine Scoring Implementation

- [ ] 2.1 Add `calculate_buy_scoring` method in `demark/engine.py` to compute Relative Volume (RVOL), Relative Volume Score, News Intensity Score, and Combined Importance Score
- [ ] 2.2 Add comprehensive unit tests in `tests/test_scoring.py` to verify volume scoring, news scoring, and combined weighted scoring logic for all tickers

## 3. Scanner Output and Sorting Implementation

- [ ] 3.1 Update `run_scanner` in `demark/cli.py` to calculate scores for each ticker in the scan list
- [ ] 3.2 Add the new Importance Score column to the scanner's CLI table output
- [ ] 3.3 Sort final scanned signals by Combined Importance Score in descending order in both the CLI printed table and the exported CSV file
- [ ] 3.4 Verify sorting and score accuracy using integration tests
