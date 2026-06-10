#!/usr/bin/env python3
"""
Run full DeMark scan on all tickers with progress output
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from send_email_results import run_scanner_and_collect_signals, format_html_table, send_email_via_mailgun
from datetime import datetime

print("=" * 80)
print("DeMark Full Scanner - All 1600+ Tickers")
print("=" * 80)
print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Run the full scanner
df_signals = run_scanner_and_collect_signals('line.txt', interval='1d', period='1y')

print()
print("=" * 80)
if df_signals is not None:
    print(f"✓ RESULTS: Found {len(df_signals)} signals")
    print("=" * 80)
    print(df_signals[['Ticker', 'Price', 'Action', 'Score']].to_string(index=False))
else:
    print("✗ RESULTS: No signals found")
    print("=" * 80)

print()
print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Send email
print()
print("Sending email...")
to_email = 'ggoni@anticiparte.cl'
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

if df_signals is not None and not df_signals.empty:
    subject = f"DeMark Scanner Results - {datetime.now().strftime('%Y-%m-%d')} ({len(df_signals)} signals)"
    html_table = format_html_table(df_signals)
else:
    subject = f"DeMark Scanner Results - {datetime.now().strftime('%Y-%m-%d')} (No signals)"
    html_table = "<p>No BUY or SELL signals found.</p>"

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

success = send_email_via_mailgun(to_email, subject, html_body)

if success:
    print(f"✓ Email sent successfully!")
else:
    print(f"✗ Failed to send email")

print("=" * 80)
