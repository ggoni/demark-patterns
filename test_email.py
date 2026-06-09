#!/usr/bin/env python3
"""
Test script for email functionality without running full scan.
"""

import os
import sys
from datetime import datetime
import pandas as pd

# Add the project to path
sys.path.insert(0, os.path.dirname(__file__))

from send_email_results import format_html_table, send_email_via_mailgun


def test_email():
    """Test email sending with mock data."""
    
    # Create mock signals
    mock_signals = {
        'Ticker': ['AAPL', 'MSFT', 'GOOGL'],
        'Price': ['150.50', '320.75', '140.25'],
        'Support': ['148.00', '315.50', '138.00'],
        'Resist': ['155.00', '325.50', '145.00'],
        'Action': ['BUY', 'SELL', 'BUY'],
        'Score': ['8.75', '7.25', '8.50'],
        'ScoreVal': [8.75, 7.25, 8.50]
    }
    
    df_signals = pd.DataFrame(mock_signals)
    
    print("Test DeMark Email Results")
    print("========================")
    print(f"Mock signals DataFrame:")
    print(df_signals)
    print()
    
    # Test HTML formatting
    html_table = format_html_table(df_signals)
    print(f"HTML Table generated: {len(html_table)} chars")
    
    # Prepare email
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    to_email = 'ggoni@anticiparte.cl'
    subject = f"DeMark Scanner Test Results - {datetime.now().strftime('%Y-%m-%d')} ({len(df_signals)} signals)"
    
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
        <h1>DeMark Scanner Test Results</h1>
        <p class="timestamp">Generated: {timestamp}</p>
        
        <div class="summary">
            <p><strong>Summary:</strong> Found {len(df_signals)} test signals</p>
        </div>
        
        {html_table}
        
        <p style="margin-top: 30px; color: #7f8c8d; font-size: 12px;">
            This is a test email from DeMark Scanner. Please do not reply to this message.
        </p>
    </body>
    </html>
    """
    
    print(f"\nEmail Details:")
    print(f"  To: {to_email}")
    print(f"  Subject: {subject}")
    print(f"  Body length: {len(html_body)} chars")
    print()
    
    # Send email
    print("Sending email via Mailgun...")
    success = send_email_via_mailgun(to_email, subject, html_body)
    
    if success:
        print("\n✓ Test passed! Email sent successfully.")
        return 0
    else:
        print("\n✗ Test failed! Email could not be sent.")
        return 1


if __name__ == "__main__":
    sys.exit(test_email())
