## ADDED Requirements

### Requirement: Fetch Top N Daily Losers
The system SHALL fetch the top N daily loser ticker symbols from Yahoo Finance using `yfinance`'s built-in screener and return them as a list of strings.

#### Scenario: Default fetch returns 10 tickers
- **WHEN** `fetch_losers()` is called with no arguments (or `n=10`)
- **THEN** the system returns a list of up to 10 ticker symbols sorted by greatest percentage loss

#### Scenario: Custom N respected
- **WHEN** `fetch_losers(n=5)` is called
- **THEN** the system returns at most 5 ticker symbols

#### Scenario: Fewer results than N available
- **WHEN** the screener returns fewer tickers than the requested N
- **THEN** the system returns all available tickers without error

#### Scenario: Screener unavailable
- **WHEN** the `yfinance` screener raises an exception (network error, rate limit, API change)
- **THEN** the system raises a `RuntimeError` with a human-readable message

### Requirement: Screener Uses yfinance Built-in
The system SHALL use `yfinance`'s `screen("day_losers")` API and SHALL NOT make direct HTTP requests or parse HTML from Yahoo Finance pages.

#### Scenario: No extra dependencies introduced
- **WHEN** the `fetch_losers` method is implemented
- **THEN** no new packages beyond those already in `requirements.txt` are imported
