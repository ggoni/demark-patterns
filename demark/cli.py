import argparse
from datetime import datetime
from demark.providers import YFinanceProvider
from demark.engine import DeMarkEngine
import matplotlib.pyplot as plt

def main():
    parser = argparse.ArgumentParser(description="DeMark Indicators Analysis Tool")
    parser.add_argument("--ticker", type=str, required=True, help="Stock ticker (e.g., AAPL)")
    parser.add_argument("--interval", type=str, default="1d", help="Data interval (1m, 1h, 1d, 1wk)")
    parser.add_argument("--period", type=str, default="1y", help="Data period (1mo, 6mo, 1y, max)")
    parser.add_argument("--plot", action="store_true", help="Plot the results")
    
    args = parser.parse_args()
    
    print(f"Fetching data for {args.ticker}...")
    provider = YFinanceProvider()
    try:
        df = provider.fetch_data(args.ticker, interval=args.interval, period=args.period)
    except Exception as e:
        print(f"Error: {e}")
        return

    print("Calculating DeMark indicators...")
    engine = DeMarkEngine(df)
    results = engine.run_all()
    
    # Formatted output
    print("\nRecent Analysis Results (Last 15 bars):")

    display_df = results.tail(15).copy()
    display_cols = {
        'Close': 'Price',
        'buy_setup_count': 'B-Setup',
        'sell_setup_count': 'S-Setup',
        'buy_countdown_count': 'B-CD',
        'sell_countdown_count': 'S-CD',
        'tdst_support': 'Support',
        'tdst_resistance': 'Resist',
        'recommendation': 'Action',
    }

    table_df = display_df[list(display_cols.keys())].rename(columns=display_cols)
    table_df = table_df.replace(0, '')

    # ANSI color helpers
    GREEN  = '\033[92m'
    RED    = '\033[91m'
    YELLOW = '\033[93m'
    RESET  = '\033[0m'

    def colorize(val):
        if val == 'BUY':  return f"{GREEN}{val}{RESET}"
        if val == 'SELL': return f"{RED}{val}{RESET}"
        return f"{YELLOW}{val}{RESET}"

    # Print header manually so we can colour the Action column
    raw = table_df.to_string()
    lines = raw.split('\n')
    for line in lines:
        if any(a in line for a in ('BUY', 'SELL', 'HOLD')):
            for action in ('BUY', 'SELL', 'HOLD'):
                line = line.replace(action, colorize(action))
        print(line)

    # Prominent recommendation for the latest bar
    last_rec = results.iloc[-1]['recommendation']
    color = GREEN if last_rec == 'BUY' else (RED if last_rec == 'SELL' else YELLOW)
    print(f"\n{'='*40}")
    print(f"  RECOMMENDATION: {color}{last_rec}{RESET}")
    print(f"{'='*40}")

    if args.plot:
        plot_results(results, args.ticker)

def plot_results(df, ticker):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True, gridspec_kw={'height_ratios': [3, 1]})
    
    # Top plot: Price and TDST
    ax1.plot(df.index, df['Close'], label='Close', color='black', alpha=0.6)
    if 'tdst_support' in df.columns:
        ax1.plot(df.index, df['tdst_support'], label='TDST Support', color='green', linestyle='--')
    if 'tdst_resistance' in df.columns:
        ax1.plot(df.index, df['tdst_resistance'], label='TDST Resist', color='red', linestyle='--')

    # Bollinger Bands overlay
    if 'bb_upper' in df.columns:
        ax1.plot(df.index, df['bb_upper'],   color='steelblue', linewidth=0.8, linestyle='--', label='BB Upper')
        ax1.plot(df.index, df['bb_middle'],  color='steelblue', linewidth=1.0, label='BB SMA-20')
        ax1.plot(df.index, df['bb_lower'],   color='steelblue', linewidth=0.8, linestyle='--', label='BB Lower')
        ax1.fill_between(df.index, df['bb_upper'], df['bb_lower'], alpha=0.08, color='steelblue')

    # Annotate counts
    for i in range(len(df)):
        if df.iloc[i]['buy_setup_count'] > 0:
            ax1.annotate(str(int(df.iloc[i]['buy_setup_count'])), (df.index[i], df.iloc[i]['Low']), 
                        textcoords="offset points", xytext=(0,-10), ha='center', color='green', fontsize=8)
        if df.iloc[i]['sell_setup_count'] > 0:
            ax1.annotate(str(int(df.iloc[i]['sell_setup_count'])), (df.index[i], df.iloc[i]['High']), 
                        textcoords="offset points", xytext=(0,10), ha='center', color='red', fontsize=8)
                        
    ax1.set_title(f"{ticker} DeMark Analysis")
    ax1.legend()
    
    # Bottom plot: Countdown
    ax2.bar(df.index, df['buy_countdown_count'], color='green', alpha=0.3, label='Buy CD')
    ax2.bar(df.index, df['sell_countdown_count'], color='red', alpha=0.3, label='Sell CD')
    ax2.set_ylabel("Countdown")
    
    plt.tight_layout()
    date_str  = datetime.now().strftime('%y%m%d')
    plot_path = f"{ticker}_{date_str}.png"
    plt.savefig(plot_path)
    print(f"\nPlot saved to {plot_path}")

if __name__ == "__main__":
    main()
