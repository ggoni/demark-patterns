import argparse
import os
from datetime import datetime
from demark.providers import YFinanceProvider
from demark.engine import DeMarkEngine
import plotly.graph_objects as go
import pandas as pd


def _plot_x_values(values):
    if hasattr(values, "to_pydatetime"):
        return values.to_pydatetime().tolist()
    return values

def main():
    parser = argparse.ArgumentParser(description="DeMark Indicators Analysis Tool")
    parser.add_argument("--ticker", type=str, help="Stock ticker (e.g., AAPL)")
    parser.add_argument("--scan", type=str, help="Path to a text file with a list of tickers to scan")
    parser.add_argument("--interval", type=str, default="1d", help="Data interval (1m, 1h, 1d, 1wk)")
    parser.add_argument("--period", type=str, default="1y", help="Data period (1mo, 6mo, 1y, max)")
    parser.add_argument("--plot", action="store_true", help="Plot the results")
    parser.add_argument(
        "--plot-output-mode",
        choices=["png", "html", "both"],
        default="png",
        help="Plot output mode when --plot is used: png, html, or both",
    )
    parser.add_argument("--no-save", action="store_true", help="Do not save CSV/plot files to disk")
    parser.add_argument(
        "--debug-setups",
        action="store_true",
        help="Print setup diagnostics to explain TDST support/resistance availability",
    )
    parser.add_argument("--output", type=str, help="Custom output path for scan results CSV")
    
    args = parser.parse_args()
    
    if not args.ticker and not args.scan:
        parser.error("Either --ticker or --scan must be provided")

    if args.scan:
        run_scanner(args)
        return

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
        if val == 'BUY':
            return f"{GREEN}{val}{RESET}"
        if val == 'SELL':
            return f"{RED}{val}{RESET}"
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

    if args.debug_setups:
        print_setup_diagnostics(results)

    if not args.no_save:
        output_dir = "analysis"
        os.makedirs(output_dir, exist_ok=True)
        
        save_to_csv(results, args.ticker, output_dir)
        
        if args.plot:
            plot_results(results, args.ticker, output_dir, output_mode=args.plot_output_mode)
    elif args.plot:
        plot_results(results, args.ticker, output_mode=args.plot_output_mode)

def load_tickers_from_file(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Scanner file not found: {file_path}")
    with open(file_path, "r") as f:
        content = f.read()
    # Split by whitespace (covers spaces, tabs, newlines)
    tickers = [t.strip() for t in content.split() if t.strip()]
    return sorted(list(set(tickers)))

def run_scanner(args):
    try:
        tickers = load_tickers_from_file(args.scan)
    except Exception as e:
        print(f"Error loading scanner file: {e}")
        return

    total = len(tickers)
    print(f"Scanning {total} tickers from {args.scan}...")
    
    signals = []
    provider = YFinanceProvider()
    
    # ANSI color helpers
    GREEN  = '\033[92m'
    RED    = '\033[91m'
    RESET  = '\033[0m'

    for i, ticker in enumerate(tickers, 1):
        print(f"Scanning {i}/{total}: {ticker}...", end='\r')
            
        try:
            df = provider.fetch_data(ticker, interval=args.interval, period=args.period)
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
                    'ScoreVal': score
                }
                signals.append(signal_data)
        except Exception:
            continue

    # Clear progress line
    print(" " * 60, end='\r')
    
    if not signals:
        print(f"\nScan complete. No BUY or SELL signals found among {total} tickers.")
    else:
        print(f"\nScan complete. Found {len(signals)} signals among {total} tickers.")
        
        # Sort final scanned signals by Combined Importance Score in descending order
        signals.sort(key=lambda s: s['ScoreVal'], reverse=True)
        
        # Print sorted summary table
        print(f"\n{'Ticker':<10} {'Price':<10} {'Support':<10} {'Resist':<10} {'Action':<22} {'Score'}")
        print("-" * 70)
        for sig in signals:
            color = GREEN if sig['Action'].startswith("BUY") else RED
            action_str = f"{sig['Action']:<22}"
            action_colored = f"{color}{action_str}{RESET}"
            print(f"{sig['Ticker']:<10} {sig['Price']:<10} {sig['Support']:<10} {sig['Resist']:<10} {action_colored} {sig['Score']}")
        print("-" * 70)
        
        # Save to file (drop the auxiliary sorting key)
        output_dir = "analysis"
        os.makedirs(output_dir, exist_ok=True)
        
        if args.output:
            out_path = args.output
        else:
            date_str = datetime.now().strftime('%y%m%d_%H%M%S')
            out_path = os.path.join(output_dir, f"scan_results_{date_str}.csv")
            
        df_export = pd.DataFrame(signals).drop(columns=['ScoreVal'], errors='ignore')
        df_export.to_csv(out_path, index=False)
        print(f"Results saved to {out_path}")

def save_to_csv(df, ticker, output_dir):
    date_str = datetime.now().strftime('%y%m%d')
    filename = f"{ticker}_{date_str}.csv"
    path = os.path.join(output_dir, filename)
    df.to_csv(path)
    print(f"Analysis persisted to {path}")

def _build_plotly_figure(df, ticker):
    fig = go.Figure()
    x_values = _plot_x_values(df.index)

    # Top panel traces: price, TDST, and optional Bollinger Bands.
    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=df["Close"],
            mode="lines",
            name="Close",
            line={"color": "black", "width": 1.5},
            opacity=0.7,
            yaxis="y1",
        )
    )

    if "tdst_support" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=df["tdst_support"],
                mode="lines",
                name="TDST Support",
                line={"color": "green", "dash": "dash"},
                yaxis="y1",
            )
        )

    if "tdst_resistance" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=df["tdst_resistance"],
                mode="lines",
                name="TDST Resist",
                line={"color": "red", "dash": "dash"},
                yaxis="y1",
            )
        )

    if {"bb_upper", "bb_middle", "bb_lower"}.issubset(df.columns):
        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=df["bb_upper"],
                mode="lines",
                name="BB Upper",
                line={"color": "steelblue", "dash": "dash", "width": 1},
                yaxis="y1",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=df["bb_lower"],
                mode="lines",
                name="BB Lower",
                line={"color": "steelblue", "dash": "dash", "width": 1},
                fill="tonexty",
                fillcolor="rgba(70,130,180,0.08)",
                yaxis="y1",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=df["bb_middle"],
                mode="lines",
                name="BB SMA-20",
                line={"color": "steelblue", "width": 1.2},
                yaxis="y1",
            )
        )

    # Setup annotations near highs/lows.
    if {"buy_setup_count", "Low"}.issubset(df.columns):
        buy_mask = df["buy_setup_count"] > 0
        if buy_mask.any():
            fig.add_trace(
                go.Scatter(
                    x=_plot_x_values(df.index[buy_mask]),
                    y=df.loc[buy_mask, "Low"],
                    mode="text",
                    text=df.loc[buy_mask, "buy_setup_count"].astype(int).astype(str),
                    textposition="bottom center",
                    textfont={"color": "green", "size": 10},
                    name="Buy Setup Count",
                    yaxis="y1",
                )
            )

    if {"sell_setup_count", "High"}.issubset(df.columns):
        sell_mask = df["sell_setup_count"] > 0
        if sell_mask.any():
            fig.add_trace(
                go.Scatter(
                    x=_plot_x_values(df.index[sell_mask]),
                    y=df.loc[sell_mask, "High"],
                    mode="text",
                    text=df.loc[sell_mask, "sell_setup_count"].astype(int).astype(str),
                    textposition="top center",
                    textfont={"color": "red", "size": 10},
                    name="Sell Setup Count",
                    yaxis="y1",
                )
            )

    # Bottom panel: countdown bars.
    fig.add_trace(
        go.Bar(
            x=x_values,
            y=df.get("buy_countdown_count", 0),
            name="Buy CD",
            marker_color="rgba(0,128,0,0.35)",
            yaxis="y2",
        )
    )
    fig.add_trace(
        go.Bar(
            x=x_values,
            y=df.get("sell_countdown_count", 0),
            name="Sell CD",
            marker_color="rgba(255,0,0,0.35)",
            yaxis="y2",
        )
    )

    fig.update_layout(
        title=f"{ticker} DeMark Analysis",
        barmode="overlay",
        hovermode="x unified",
        xaxis={"domain": [0.0, 1.0], "anchor": "y1"},
        yaxis={"domain": [0.28, 1.0], "title": "Price"},
        yaxis2={"domain": [0.0, 0.22], "title": "Countdown"},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0},
        margin={"l": 50, "r": 30, "t": 70, "b": 40},
    )
    return fig


def plot_results(df, ticker, output_dir=".", output_mode="png"):
    fig = _build_plotly_figure(df, ticker)
    date_str = datetime.now().strftime("%y%m%d")

    if output_mode in {"html", "both"}:
        html_path = os.path.join(output_dir, f"{ticker}_{date_str}.html")
        fig.write_html(html_path, include_plotlyjs=True, full_html=True)
        print(f"Plot saved to {html_path}")

    if output_mode in {"png", "both"}:
        png_path = os.path.join(output_dir, f"{ticker}_{date_str}.png")
        fig.write_image(png_path)
        print(f"Plot saved to {png_path}")


def print_setup_diagnostics(results):
    buy_9_idx = results.index[results['buy_setup_count'] == 9]
    sell_9_idx = results.index[results['sell_setup_count'] == 9]

    print("\nSetup diagnostics:")
    print(f"- Buy Setup 9 completions: {len(buy_9_idx)}")
    print(f"- Sell Setup 9 completions: {len(sell_9_idx)}")

    if len(buy_9_idx) > 0:
        print(f"- Latest Buy Setup 9: {buy_9_idx[-1]}")
    if len(sell_9_idx) > 0:
        print(f"- Latest Sell Setup 9: {sell_9_idx[-1]}")
    else:
        print("- TDST Support remains NaN because no Sell Setup 9 completed in this window.")

    if len(buy_9_idx) == 0:
        print("- TDST Resistance remains NaN because no Buy Setup 9 completed in this window.")

if __name__ == "__main__":
    main()
