#!/usr/bin/env python3
"""Quick test to see how many tickers generate signals from a small subset."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from demark.providers import YFinanceProvider
from demark.engine import DeMarkEngine
import pandas as pd

# Test with just first 10 tickers
test_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B', 'JNJ', 'AVGO']

signals = []
provider = YFinanceProvider()

print(f"Testing {len(test_tickers)} tickers...")
for ticker in test_tickers:
    try:
        df = provider.fetch_data(ticker, interval='1d', period='1y')
        news_count = provider.fetch_news_count_24h(ticker)
        engine = DeMarkEngine(df)
        results = engine.run_all(news_count=news_count)
        
        last_row = results.iloc[-1]
        rec = last_row['recommendation']
        
        if rec.startswith("BUY") or rec.startswith("SELL"):
            price = last_row['Close']
            support = last_row['tdst_support'] if not pd.isna(last_row['tdst_support']) else None
            resist = last_row['tdst_resistance'] if not pd.isna(last_row['tdst_resistance']) else None
            score = last_row['combined_score']
            
            signal_data = {
                'Ticker': ticker,
                'Price': f"{price:.2f}",
                'Support': f"{support:.2f}" if support is not None else "N/A",
                'Resist': f"{resist:.2f}" if resist is not None else "N/A",
                'Action': rec,
                'Score': f"{score:.2f}",
            }
            signals.append(signal_data)
            print(f"  ✓ {ticker}: {rec} ({score:.2f})")
        else:
            print(f"  - {ticker}: {rec}")
    except Exception as e:
        print(f"  ✗ {ticker}: Error - {e}")

print(f"\nFound {len(signals)} signals out of {len(test_tickers)} tickers")
if signals:
    df = pd.DataFrame(signals)
    print(df.to_string())
