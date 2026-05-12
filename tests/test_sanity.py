import pandas as pd
import numpy as np

def test_sanity():
    assert True

def test_pandas_numpy():
    df = pd.DataFrame({'a': [1, 2, 3]})
    assert len(df) == 3
    assert np.mean(df['a']) == 2.0
