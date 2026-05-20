import pandas as pd
import numpy as np
import pytest
from demark.engine import DeMarkEngine

def test_volume_score_below_average():
    # Setup dataframe with 20 days of volume. Average volume = 100
    volumes = [100.0] * 19 + [50.0]  # last volume is 50.0, average is 97.5 (because last bar changes average)
    # Let's specify exact volumes to make math clean:
    # 20-day Volume SMA = 100.0. Today's volume = 50.0 -> RVOL = 0.5
    # Let's make the first 19 volumes be 102.6315..., so average is exactly 100.0.
    # Alternatively, let's just create a list of volumes:
    # 19 * 100 = 1900. Today is 50. Total = 1950. 1950 / 20 = 97.5. RVOL = 50 / 97.5 = 0.51282
    # Let's verify with explicit values:
    df = pd.DataFrame({
        'Open': [10.0] * 20,
        'High': [11.0] * 20,
        'Low': [9.0] * 20,
        'Close': [10.0] * 20,
        'Volume': [100.0] * 19 + [50.0]
    })
    engine = DeMarkEngine(df)
    score = engine.calculate_buy_scoring(news_count=0)
    
    vol_sma20 = df['Volume'].mean()  # 1950 / 20 = 97.5
    expected_rvol = 50.0 / vol_sma20  # 0.5128205
    expected_vol_score = 5.0 * expected_rvol
    expected_combined = expected_vol_score * 0.6 + 0.0 * 0.4
    
    assert pytest.approx(engine.df.iloc[-1]['vol_sma20']) == vol_sma20
    assert pytest.approx(engine.df.iloc[-1]['rvol']) == expected_rvol
    assert pytest.approx(engine.df.iloc[-1]['volume_score']) == expected_vol_score
    assert pytest.approx(engine.df.iloc[-1]['news_score']) == 0.0
    assert pytest.approx(engine.df.iloc[-1]['combined_score']) == expected_combined
    assert pytest.approx(score) == expected_combined

def test_volume_score_above_average_uncapped():
    # 20-day Volume SMA = 100.0. Today's volume = 150.0 -> RVOL = 1.5
    # Let's specify volumes so that SMA is exactly 100
    # 19 * 97.3684... + 150 = 2000 -> 2000 / 20 = 100.0. Let's let pandas compute it.
    df = pd.DataFrame({
        'Open': [10.0] * 20,
        'High': [11.0] * 20,
        'Low': [9.0] * 20,
        'Close': [10.0] * 20,
        'Volume': [100.0] * 19 + [150.0]
    })
    engine = DeMarkEngine(df)
    score = engine.calculate_buy_scoring(news_count=0)
    
    vol_sma20 = df['Volume'].mean()  # 2050 / 20 = 102.5
    expected_rvol = 150.0 / vol_sma20  # 1.4634146
    expected_vol_score = 5.0 + 2.5 * (expected_rvol - 1.0)
    expected_combined = expected_vol_score * 0.6 + 0.0 * 0.4
    
    assert pytest.approx(engine.df.iloc[-1]['vol_sma20']) == vol_sma20
    assert pytest.approx(engine.df.iloc[-1]['rvol']) == expected_rvol
    assert pytest.approx(engine.df.iloc[-1]['volume_score']) == expected_vol_score
    assert pytest.approx(score) == expected_combined

def test_volume_score_above_average_capped():
    # RVOL is very high (e.g. 5.0) -> volume score should be capped at 10.0
    df = pd.DataFrame({
        'Open': [10.0] * 20,
        'High': [11.0] * 20,
        'Low': [9.0] * 20,
        'Close': [10.0] * 20,
        'Volume': [100.0] * 19 + [1000.0]
    })
    engine = DeMarkEngine(df)
    score = engine.calculate_buy_scoring(news_count=0)
    
    assert engine.df.iloc[-1]['volume_score'] == 10.0
    assert pytest.approx(score) == 6.0  # 10.0 * 0.6 + 0.0 * 0.4

def test_news_intensity_scoring():
    df = pd.DataFrame({
        'Open': [10.0] * 20,
        'High': [11.0] * 20,
        'Low': [9.0] * 20,
        'Close': [10.0] * 20,
        'Volume': [100.0] * 20
    })
    
    # 0 articles
    engine = DeMarkEngine(df)
    score_0 = engine.calculate_buy_scoring(news_count=0)
    assert engine.df.iloc[-1]['news_score'] == 0.0
    assert pytest.approx(score_0) == 3.0  # Vol score is 5.0 (since RVOL = 1.0) -> 5.0 * 0.6 = 3.0
    
    # 3 articles (between 1 and 5) -> News score = 6.0
    engine = DeMarkEngine(df)
    score_3 = engine.calculate_buy_scoring(news_count=3)
    assert engine.df.iloc[-1]['news_score'] == 6.0
    assert pytest.approx(score_3) == 5.4  # 5.0 * 0.6 + 6.0 * 0.4 = 3.0 + 2.4 = 5.4
    
    # 6 articles (greater than 5) -> News score = 10.0
    engine = DeMarkEngine(df)
    score_6 = engine.calculate_buy_scoring(news_count=6)
    assert engine.df.iloc[-1]['news_score'] == 10.0
    assert pytest.approx(score_6) == 7.0  # 5.0 * 0.6 + 10.0 * 0.4 = 3.0 + 4.0 = 7.0
