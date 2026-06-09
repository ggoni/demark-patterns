#!/usr/bin/env python3
"""
Script to run DeMark scanner and send results via Mailgun email.
Usage: python send_email_results.py
"""

import os
import sys
from datetime import datetime
import requests
from pathlib import Path

# Add the project to path so we can import demark
sys.path.insert(0, str(Path(__file__).parent))

from demark.providers import YFinanceProvider
from demark.engine import DeMarkEngine
import pandas as pd


def load_tickers_from_file(file_path):
    """Load tickers from a text file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Scanner file not found: {file_path}")
    with open(file_path, "r") as f:
        content = f.read()
    tickers = [t.strip() for t in content.split() if t.strip()]
    return sorted(list(set(tickers)))


def run_scanner_and_collect_signals(ticker_file, interval="1d", period="1y"):
    """
    Run scanner on tickers and return signals DataFrame.
    Returns: pandas DataFrame with signals or None if no signals found.
    """
    try:
        tickers = load_tickers_from_file(ticker_file)
    except Exception as e:
        print(f"Error loading scanner file: {e}")
        return None

    total = len(tickers)
    print(f"Scanning {total} tickers from {ticker_file}...")

    signals = []
    provider = YFinanceProvider()

    for i, ticker in enumerate(tickers, 1):
        print(f"Scanning {i}/{total}: {ticker}...", end='\r')

        try:
            df = provider.fetch_data(ticker, interval=interval, period=period)
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
        except Exception as e:
            print(f"Error processing {ticker}: {e}", file=sys.stderr)
            continue

    # Clear progress line
    print(" " * 60, end='\r')

    if not signals:
        print(f"Scan complete. No BUY or SELL signals found among {total} tickers.")
        return None

    # Sort by Combined Importance Score descending
    signals.sort(key=lambda s: s['ScoreVal'], reverse=True)

    # Convert to DataFrame for easier handling
    df_signals = pd.DataFrame(signals)
    
    print(f"Scan complete. Found {len(df_signals)} signals among {total} tickers.")
    print("\nSignals found:")
    print(df_signals[['Ticker', 'Price', 'Action', 'Score']].to_string(index=False))

    return df_signals


def format_html_table(df_signals):
    """Convert DataFrame to HTML table."""
    if df_signals is None or df_signals.empty:
        return "<p>No signals found.</p>"
    
    # Remove the ScoreVal column before displaying
    display_df = df_signals.drop(columns=['ScoreVal'], errors='ignore')
    
    html = display_df.to_html(index=False, border=0)
    
    # Add some basic styling
    styled_html = f"""
    <table style="border-collapse: collapse; width: 100%; font-family: Arial, sans-serif; margin: 20px 0;">
        <thead>
            <tr style="background-color: #f0f0f0; border-bottom: 2px solid #333;">
                <th style="padding: 12px; text-align: left; border-right: 1px solid #ccc;">Ticker</th>
                <th style="padding: 12px; text-align: left; border-right: 1px solid #ccc;">Price</th>
                <th style="padding: 12px; text-align: left; border-right: 1px solid #ccc;">Support</th>
                <th style="padding: 12px; text-align: left; border-right: 1px solid #ccc;">Resist</th>
                <th style="padding: 12px; text-align: left; border-right: 1px solid #ccc;">Action</th>
                <th style="padding: 12px; text-align: left;">Score</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for idx, row in display_df.iterrows():
        action_style = 'color: green; font-weight: bold;' if row['Action'].startswith('BUY') else 'color: red; font-weight: bold;'
        styled_html += f"""
            <tr style="border-bottom: 1px solid #ddd;">
                <td style="padding: 10px; border-right: 1px solid #ddd;">{row['Ticker']}</td>
                <td style="padding: 10px; border-right: 1px solid #ddd;">{row['Price']}</td>
                <td style="padding: 10px; border-right: 1px solid #ddd;">{row['Support']}</td>
                <td style="padding: 10px; border-right: 1px solid #ddd;">{row['Resist']}</td>
                <td style="padding: 10px; border-right: 1px solid #ddd; {action_style}">{row['Action']}</td>
                <td style="padding: 10px;">{row['Score']}</td>
            </tr>
        """
    
    styled_html += """
        </tbody>
    </table>
    """
    
    return styled_html


def send_email_via_mailgun(to_email, subject, html_body):
    """Send email using Mailgun API."""
    # Get Mailgun credentials from environment
    api_key = os.getenv('MAILGUN_API_KEY')
    domain = os.getenv('MAILGUN_DOMAIN')
    
    if not api_key or not domain:
        print("Error: MAILGUN_API_KEY or MAILGUN_DOMAIN environment variables not set")
        return False
    
    from_email = f"noreply@{domain}"
    
    # Mailgun API endpoint
    url = f"https://api.mailgun.net/v3/{domain}/messages"
    
    # Prepare the request
    auth = ("api", api_key)
    data = {
        "from": from_email,
        "to": to_email,
        "subject": subject,
        "html": html_body
    }
    
    try:
        response = requests.post(url, auth=auth, data=data)
        response.raise_for_status()
        print(f"✓ Email sent successfully to {to_email}")
        print(f"  Message ID: {response.json().get('id')}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to send email: {e}")
        if hasattr(e.response, 'text'):
            print(f"  Response: {e.response.text}")
        return False


def main():
    """Main entry point."""
    # Get environment variables
    scanner_file = os.getenv('DEMARK_SCANNER_FILE', 'line.txt')
    to_email = os.getenv('DEMARK_EMAIL_TO', 'ggoni@anticiparte.cl')
    interval = os.getenv('DEMARK_INTERVAL', '1d')
    period = os.getenv('DEMARK_PERIOD', '1y')
    
    print(f"DeMark Scanner with Email Results")
    print(f"================================")
    print(f"Scanner file: {scanner_file}")
    print(f"Email to: {to_email}")
    print(f"Interval: {interval}, Period: {period}")
    print()
    
    # Run scanner
    df_signals = run_scanner_and_collect_signals(scanner_file, interval=interval, period=period)
    
    # Prepare email
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if df_signals is not None and not df_signals.empty:
        subject = f"DeMark Scanner Results - {datetime.now().strftime('%Y-%m-%d')} ({len(df_signals)} signals)"
        html_table = format_html_table(df_signals)
    else:
        subject = f"DeMark Scanner Results - {datetime.now().strftime('%Y-%m-%d')} (No signals)"
        html_table = "<p>No BUY or SELL signals found in the latest scan.</p>"
    
    # Build complete email body
    html_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; color: #333; }}
            h1 {{ color: #2c3e50; }}
            .timestamp {{ color: #7f8c8d; font-size: 12px; }}
            .summary {{ background-color: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <h1>DeMark Scanner Results</h1>
        <p class="timestamp">Generated: {timestamp}</p>
        
        <div class="summary">
            <p><strong>Summary:</strong> {f"Found {len(df_signals)} signals" if df_signals is not None else "No signals found"}</p>
        </div>
        
        {html_table}
        
        <p style="margin-top: 30px; color: #7f8c8d; font-size: 12px;">
            This is an automated email from DeMark Scanner. Please do not reply to this message.
        </p>
    </body>
    </html>
    """
    
    # Send email
    success = send_email_via_mailgun(to_email, subject, html_body)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
