import os
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock
from demark import cli

@patch("demark.cli.load_tickers_from_file")
@patch("demark.cli.YFinanceProvider")
@patch("demark.cli.DeMarkEngine")
def test_scanner_sorting_and_export(mock_engine_cls, mock_provider_cls, mock_load_tickers, tmp_path):
    # 1. Setup mocked tickers
    mock_load_tickers.return_value = ["T1", "T2", "T3"]
    
    # 2. Setup mock provider behaviour
    provider = mock_provider_cls.return_value
    provider.fetch_data.return_value = pd.DataFrame({
        "Open": [10.0] * 20,
        "High": [11.0] * 20,
        "Low": [9.0] * 20,
        "Close": [10.0] * 20,
        "Volume": [100.0] * 20
    })
    
    # News counts to return: T1 -> 0, T2 -> 3, T3 -> 6
    def mock_fetch_news_count(ticker):
        if ticker == "T1":
            return 0
        elif ticker == "T2":
            return 3
        else:
            return 6
    provider.fetch_news_count_24h.side_effect = mock_fetch_news_count
    
    # 3. Setup mock engines and their run_all return dataframes
    # We want T3 to have score 7.0, T2 to have 5.4, T1 to have 3.0
    # And all of them to trigger signals
    t1_df = pd.DataFrame({
        "Close": [10.0],
        "tdst_support": [9.0],
        "tdst_resistance": [11.0],
        "recommendation": ["BUY (Setup Complete)"],
        "combined_score": [3.0]
    })
    
    t2_df = pd.DataFrame({
        "Close": [20.0],
        "tdst_support": [18.0],
        "tdst_resistance": [22.0],
        "recommendation": ["SELL (Setup Complete)"],
        "combined_score": [5.4]
    })
    
    t3_df = pd.DataFrame({
        "Close": [30.0],
        "tdst_support": [27.0],
        "tdst_resistance": [33.0],
        "recommendation": ["BUY (Oversold)"],
        "combined_score": [7.0]
    })
    
    # MagicMock to return different results based on the dataframe passed in
    def mock_engine_init(df):
        engine = MagicMock()
        # Look at the close price of the mock df passed to determine which ticker it is
        first_close = df["Close"].iloc[0]
        if first_close == 10.0:
            engine.run_all.return_value = t1_df
        elif first_close == 20.0:
            engine.run_all.return_value = t2_df
        else:
            engine.run_all.return_value = t3_df
        return engine
        
    mock_engine_cls.side_effect = mock_engine_init
    
    # Since run_scanner uses provider.fetch_data which returns df,
    # let's map the input ticker to returns containing close prices 10, 20, 30
    def mock_fetch_data(ticker, interval=None, period=None):
        if ticker == "T1":
            close_val = 10.0
        elif ticker == "T2":
            close_val = 20.0
        else:
            close_val = 30.0
        return pd.DataFrame({
            "Open": [close_val] * 20,
            "High": [close_val + 1.0] * 20,
            "Low": [close_val - 1.0] * 20,
            "Close": [close_val] * 20,
            "Volume": [100.0] * 20
        })
    provider.fetch_data.side_effect = mock_fetch_data

    # 4. Prepare args
    args = MagicMock()
    args.scan = "mock_watchlist.txt"
    args.interval = "1d"
    args.period = "1y"
    args.output = os.path.join(tmp_path, "scan_results.csv")
    
    # 5. Execute run_scanner
    cli.run_scanner(args)
    
    # 6. Verify CSV results
    assert os.path.exists(args.output)
    df_result = pd.read_csv(args.output)
    
    # Check structure
    expected_cols = ["Ticker", "Price", "Support", "Resist", "Action", "Score"]
    assert list(df_result.columns) == expected_cols
    
    # Check sorted order (Score descending: T3 (7.00), T2 (5.40), T1 (3.00))
    assert len(df_result) == 3
    assert df_result.iloc[0]["Ticker"] == "T3"
    assert df_result.iloc[0]["Score"] == 7.00
    assert df_result.iloc[1]["Ticker"] == "T2"
    assert df_result.iloc[1]["Score"] == 5.40
    assert df_result.iloc[2]["Ticker"] == "T1"
    assert df_result.iloc[2]["Score"] == 3.00
