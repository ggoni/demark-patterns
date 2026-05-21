from abc import ABC, abstractmethod
import pandas as pd
import yfinance as yf

class BaseProvider(ABC):
    @abstractmethod
    def fetch_data(self, ticker: str, interval: str = "1d", period: str = "1y") -> pd.DataFrame:
        """Fetch OHLCV data from the source."""
        pass

    @abstractmethod
    def fetch_news_count_24h(self, ticker: str) -> int:
        """Fetch the number of news articles in the last 24 hours for a ticker."""
        pass

    @abstractmethod
    def fetch_losers(self, n: int = 10) -> list:
        """Return up to n ticker symbols for the top daily losers."""
        pass

class YFinanceProvider(BaseProvider):
    def fetch_data(self, ticker: str, interval: str = "1d", period: str = "1y") -> pd.DataFrame:
        """Fetch OHLCV data from Yahoo Finance."""
        ticker_obj = yf.Ticker(ticker)
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        # Use repair=True for better data quality as discussed in design
        df = ticker_obj.history(period=period, interval=interval, repair=True)
        
        if df.empty:
            raise ValueError(f"No data found for ticker '{ticker}'")

        # Clean data: drop rows with all NaNs and ensure numeric types
        df = df.dropna(how='all')
        for col in required_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Ensure we have the required columns
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"Data for '{ticker}' is missing required OHLCV columns")

        # Final check for NaNs in critical columns
        if df[required_columns].isnull().any().any():
            # If NaNs remain, fill them with forward fill (standard for time series)
            df[required_columns] = df[required_columns].ffill()

        return df[required_columns]

    def fetch_losers(self, n: int = 10) -> list:
        """Return up to n ticker symbols for the top daily losers from Yahoo Finance."""
        try:
            result = yf.screen("day_losers", count=n)
            quotes = result.get("quotes", [])
            tickers = [q["symbol"] for q in quotes if "symbol" in q]
            return tickers[:min(n, len(tickers))]
        except Exception as exc:
            raise RuntimeError(
                f"Failed to fetch daily losers from Yahoo Finance: {exc}. "
                "Try: pip install --upgrade yfinance"
            ) from exc

    def fetch_news_count_24h(self, ticker: str) -> int:
        """Fetch the number of news articles in the last 24 hours from Yahoo Finance."""
        try:
            ticker_obj = yf.Ticker(ticker)
            news = ticker_obj.news
            if not news:
                return 0
            
            from datetime import datetime, timezone, timedelta
            now = datetime.now(timezone.utc)
            count = 0
            for item in news:
                pub_date_str = item.get('pubDate') or item.get('content', {}).get('pubDate')
                if pub_date_str:
                    # Clean/parse date string
                    dt = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
                    if now - dt <= timedelta(hours=24):
                        count += 1
            return count
        except Exception:
            # Fallback to 0 if endpoint fails or rate limited
            return 0

