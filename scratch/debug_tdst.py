import pandas as pd
import numpy as np
from demark.engine import DeMarkEngine

def debug_tdst():
    dates = pd.date_range("2023-01-01", periods=30)
    # Buy Setup: prices falling. Need flip first.
    # Bars 0-4: 100
    # Bar 5: 90 (Close[5]=90 < Close[1]=100). Flip: Close[4]=100 >= Close[0]=100. Count 1.
    # Bar 5 Low: 89.
    prices = [100, 100, 100, 100, 100, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81] + [81]*15
    lows = [p-1 for p in prices]
    highs = [p+1 for p in prices]
    df = pd.DataFrame({"Close": prices, "Low": lows, "High": highs}, index=dates)
    
    engine = DeMarkEngine(df)
    results = engine.run_all()
    
    # Setup 9 at index 13
    print("Row 13 (Setup 9) Resistance:", results.iloc[13]['tdst_resistance'])
    print("Row 14 Resistance:", results.iloc[14]['tdst_resistance'])
    print("Row 5 (Setup 1) Resistance:", results.iloc[5]['tdst_resistance'])
    
    if np.isnan(results.iloc[13]['tdst_resistance']):
        print("FAIL: Resistance is NaN at setup completion")
    else:
        print("SUCCESS: Resistance is set to:", results.iloc[13]['tdst_resistance'])

if __name__ == "__main__":
    debug_tdst()
