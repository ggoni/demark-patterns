import pytest
import pandas as pd
import numpy as np
from demark.engine import DeMarkEngine

@pytest.fixture
def sample_data():
    """Create a sample dataset that should trigger a Buy Setup."""
    dates = pd.date_range(start="2024-01-01", periods=20, freq='D')
    # Price is dropping: Close < Close-4
    # 100, 99, 98, 97, 96, 95...
    closes = [100 - i for i in range(20)]
    highs = [c + 1 for c in closes]
    lows = [c - 1 for c in closes]
    opens = closes
    
    return pd.DataFrame({
        'Open': opens,
        'High': highs,
        'Low': lows,
        'Close': closes,
        'Volume': [1000] * 20
    }, index=dates)

def test_setup_buy(sample_data):
    engine = DeMarkEngine(sample_data)
    df = engine.calculate_setup()
    
    # At index 4, the count should start (Close 4 < Close 0)
    # 96 < 100
    assert df.iloc[4]['buy_setup_count'] == 1
    # At index 12, we should have a 9-count (96, 95, 94, 93, 92, 91, 90, 89, 88)
    # Wait, indices:
    # 4: 1
    # 5: 2
    # 6: 3
    # 7: 4
    # 8: 5
    # 9: 6
    # 10: 7
    # 11: 8
    # 12: 9
    assert df.iloc[12]['buy_setup_count'] == 9

def test_intersection(sample_data):
    engine = DeMarkEngine(sample_data)
    engine.calculate_setup()
    df = engine.validate_intersection()
    
    # In our sample data, Highs are always dropping too.
    # Bar 8 (index 11) High is 89. Lows of 3-7 (indices 6-10) are 93, 92, 91, 90, 89.
    # High[8] (89) >= min(93, 92, 91, 90, 89) -> 89 >= 89. True.
    assert df.iloc[11]['buy_intersection'] == True
    assert df.iloc[12]['buy_intersection'] == True

def test_countdown(sample_data):
    # For countdown, we need more data.
    # After a 9-count at index 12, countdown starts.
    # We need 13 more bars of Close <= Low-2.
    # 20 bars total. Index 12 is 9-count. 13-19 are 7 bars.
    # We won't finish a countdown but we can check if it starts.
    engine = DeMarkEngine(sample_data)
    engine.calculate_setup()
    df = engine.calculate_countdown()
    
    # index 12: Count 1 (Close 88 <= Low 89)
    # index 13: Count 2 (Close 87 <= Low 88)
    # index 14: Count 3 (Close 86 <= Low 87)
    assert df.iloc[14]['buy_countdown_count'] == 3

def test_tdst(sample_data):
    engine = DeMarkEngine(sample_data)
    engine.calculate_setup()
    df = engine.calculate_tdst()
    
    # After index 12, we should have a support line.
    # Lowest low in the 9-bar setup (indices 4 to 12).
    # Index 12 Low is 87.
    assert df.iloc[12]['tdst_support'] == 87
    assert df.iloc[19]['tdst_support'] == 87
