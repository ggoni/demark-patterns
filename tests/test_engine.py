import pandas as pd
import numpy as np
from demark.engine import DeMarkEngine

def test_buy_setup_with_price_flip():
    # Setup requires a flip: close[i-1] >= close[i-5] and close[i] < close[i-4]
    dates = pd.date_range("2023-01-01", periods=15)
    # Price flip at bar 5: close[4]=100 >= close[0]=100, close[5]=90 < close[1]=100
    prices = [100, 100, 100, 100, 100, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81]
    df = pd.DataFrame({"Close": prices, "Low": [p-1 for p in prices], "High": [p+1 for p in prices]}, index=dates)
    engine = DeMarkEngine(df)
    results = engine.calculate_setup()
    
    # Bar 5 should have count 1
    assert results.iloc[5]['buy_setup_count'] == 1
    # Bar 13 should have count 9 (13 = 5 + 8)
    assert results.iloc[13]['buy_setup_count'] == 9

def test_setup_perfection():
    dates = pd.date_range("2023-01-01", periods=15)
    prices = [100, 100, 100, 100, 100, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81]
    # At index 13 (count 9): Close[13]=82.
    # Perfection: min(Low[13], Low[12]) <= min(Low[11], Low[10])
    # Lows: 99, 99, 99, 99, 99, 89, 88, 87, 86, 85, 84, 83, 82, 70, 69
    lows =   [99,  99,  99,  99,  99,  89, 88, 87, 86, 85, 84, 83, 82, 70, 69]
    df = pd.DataFrame({"Close": prices, "Low": lows, "High": [p+1 for p in prices]}, index=dates)
    engine = DeMarkEngine(df)
    results = engine.calculate_setup()
    
    assert results.iloc[13]['buy_setup_count'] == 9
    assert bool(results.iloc[13]['buy_perfect']) is True

def test_tdst_resistance_bar1():
    # Buy Setup (Downtrend) defines Resistance (High of Bar 1)
    dates = pd.date_range("2023-01-01", periods=15)
    prices = [100]*5 + [90, 89, 88, 87, 86, 85, 84, 83, 82, 81]
    highs =  [101]*5 + [91, 90, 89, 88, 87, 86, 85, 84, 83, 82] # High at bar 5 (Setup 1) is 91
    df = pd.DataFrame({"Close": prices, "Low": [p-1 for p in prices], "High": highs}, index=dates)
    engine = DeMarkEngine(df)
    results = engine.run_all()
    
    # Setup 9 is at index 13
    assert results.iloc[13]['buy_setup_count'] == 9
    assert results.iloc[13]['tdst_resistance'] == 91.0

def test_tdst_support_bar1():
    # Sell Setup (Uptrend) defines Support (Low of Bar 1)
    dates = pd.date_range("2023-01-01", periods=15)
    prices = [100]*5 + [110, 111, 112, 113, 114, 115, 116, 117, 118, 119]
    lows =   [99]*5 + [109, 110, 111, 112, 113, 114, 115, 116, 117, 118] # Low at bar 5 (Setup 1) is 109
    df = pd.DataFrame({"Close": prices, "Low": lows, "High": [p+1 for p in prices]}, index=dates)
    engine = DeMarkEngine(df)
    results = engine.run_all()
    
    # Setup 9 is at index 13
    assert results.iloc[13]['sell_setup_count'] == 9
    assert results.iloc[13]['tdst_support'] == 109.0

def test_countdown_qualification():
    # Countdown 13 requires Close[13] <= Close[8]
    n = 100
    dates = pd.date_range("2023-01-01", periods=n)
    # 1. Complete Setup (starts at 5, ends at 13)
    # Drop sharply to ensure Close <= Low[i-2]
    # Low[i-2] = Close[i-2] - 0.1
    # So we need Close[i] <= Close[i-2] - 0.1
    prices = [100]*5 + [90 - i for i in range(n-5)]
    df = pd.DataFrame({"Close": prices, "Low": [p-0.1 for p in prices], "High": [p+0.1 for p in prices]}, index=dates)
    engine = DeMarkEngine(df)
    results = engine.run_all()
    
    # Check CD 13 exists
    cd13_exists = (results['buy_countdown_count'] == 13).any()
    assert cd13_exists

def test_recommendation_crossover():
    # Price breaks resistance at index 18, should HOLD after that
    dates = pd.date_range("2023-01-01", periods=29)
    
    # 1. Price Flip for Buy Setup: Close[i-1] >= Close[i-5] and Close[i] < Close[i-4]
    # Indices 0-4: 100
    # Index 5: 90 (Flip! 100 >= 100, 90 < 100). Setup Count 1.
    prices = [100]*5 + [90, 89, 88, 87, 86, 85, 84, 83, 82] # Setup 9 finishes at index 13
    highs =  [101]*5 + [91, 90, 89, 88, 87, 86, 85, 84, 83] # Bar 1 High at index 5 is 91
    
    # Resistance should be 91.0
    # Bars 14-29: Price rises to break 91.0
    # 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92 (Break!), 93...
    prices += [83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97]
    highs  += [84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98]
    
    df = pd.DataFrame({"Close": prices, "Low": [p-1 for p in prices], "High": highs}, index=dates)
    engine = DeMarkEngine(df)
    results = engine.run_all()
    
    # Setup 9 at index 13
    assert results.iloc[13]['buy_setup_count'] == 9
    assert results.iloc[13]['tdst_resistance'] == 91.0
    
    # Find break index (Price 92 at index 14+9 = 23?)
    # Index 23: 92 > 91. Index 22: 91 <= 91.
    assert results.iloc[23]['Close'] == 92
    assert results.iloc[23]['recommendation'] == "BUY (Resistance Break)"
    assert results.iloc[24]['recommendation'] != "BUY (Resistance Break)"
