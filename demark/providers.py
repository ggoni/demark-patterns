from abc import ABC, abstractmethod
import pandas as pd
import yfinance as yf

class BaseProvider(ABC):
    @abstractmethod
    def fetch_data(self, ticker: str, interval: str = "1d", period: str = "1y") -> pd.DataFrame:
        """Fetch OHLCV data from the source."""
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
