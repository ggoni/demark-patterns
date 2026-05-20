import sys
import pandas as pd
from demark.providers import YFinanceProvider
from demark.engine import DeMarkEngine

def main():
    tickers = ["AAPL", "TSLA"]
    if len(sys.argv) > 1:
        tickers = sys.argv[1:3]
        
    print(f"Fetching news and volume data for: {tickers}...")
    provider = YFinanceProvider()
    
    data = []
    for ticker in tickers:
        try:
            df = provider.fetch_data(ticker, interval="1d", period="1mo")
            news_count = provider.fetch_news_count_24h(ticker)
            engine = DeMarkEngine(df)
            engine.run_all(news_count=news_count)
            
            last_row = engine.df.iloc[-1]
            vol_today = last_row['Volume']
            vol_sma = last_row['vol_sma20']
            rvol = last_row['rvol']
            vol_score = last_row['volume_score']
            news_score = last_row['news_score']
            combined_score = last_row['combined_score']
            
            data.append({
                'Ticker': ticker,
                'Today Vol': f"{vol_today:,.0f}",
                '20D Vol SMA': f"{vol_sma:,.0f}",
                'RVOL': f"{rvol:.2f}x",
                'Vol Score': f"{vol_score:.2f}/10",
                'News Count': f"{news_count}",
                'News Score': f"{news_score:.2f}/10",
                'Combined Score': f"{combined_score:.2f}/10"
            })
        except Exception as e:
            print(f"Error fetching/calculating for {ticker}: {e}")
            
    if data:
        # Print a clean, beautiful summary table (Nothing Style)
        print("\n" + "="*80)
        print(f"{'Ticker':<8} | {'Today Vol':<12} | {'20D SMA':<12} | {'RVOL':<6} | {'Vol Sc':<8} | {'News':<5} | {'News Sc':<8} | {'Final'}")
        print("-"*80)
        for d in data:
            print(f"{d['Ticker']:<8} | {d['Today Vol']:<12} | {d['20D Vol SMA']:<12} | {d['RVOL']:<6} | {d['Vol Score']:<8} | {d['News Count']:<5} | {d['News Score']:<8} | {d['Combined Score']}")
        print("="*80)
        print("\nFormula details:")
        print("- Volume Score: 5.0 * RVOL (if RVOL < 1), else 5.0 + 2.5 * (RVOL - 1) (capped at 10.0)")
        print("- News Score: 0.5 * News Count in last 24h (capped at 10.0)")
        print("- Combined Score: (Volume Score * 0.6) + (News Score * 0.4)")
        print("="*80 + "\n")

if __name__ == "__main__":
    main()
