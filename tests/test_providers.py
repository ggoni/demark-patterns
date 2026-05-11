import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from demark.providers import YFinanceProvider

@pytest.fixture
def provider():
    return YFinanceProvider()

@patch('yfinance.Ticker')
def test_fetch_data_success(mock_ticker, provider):
    # Setup mock data
    mock_df = pd.DataFrame({
        'Open': [100.0, 101.0],
        'High': [102.0, 103.0],
        'Low': [99.0, 100.0],
        'Close': [101.5, 102.5],
        'Volume': [1000, 1100]
    })
    mock_ticker.return_value.history.return_value = mock_df
    
    result = provider.fetch_data("AAPL")
    
    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == ['Open', 'High', 'Low', 'Close', 'Volume']
    assert len(result) == 2
    mock_ticker.return_value.history.assert_called_once()

@patch('yfinance.Ticker')
def test_fetch_data_empty(mock_ticker, provider):
    mock_ticker.return_value.history.return_value = pd.DataFrame()
    
    with pytest.raises(ValueError, match="No data found"):
        provider.fetch_data("INVALID")

@patch('yfinance.Ticker')
def test_fetch_data_missing_columns(mock_ticker, provider):
    mock_df = pd.DataFrame({'Open': [100], 'Close': [101]})
    mock_ticker.return_value.history.return_value = mock_df
    
    with pytest.raises(ValueError, match="missing required OHLCV columns"):
        provider.fetch_data("AAPL")
