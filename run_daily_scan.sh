#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

# Load secrets
set -a; source /data/.secrets/demark.env; set +a

SCAN_FILE="${1:-line.txt}"
REPORT_DIR="analysis"

echo "=== DeMark Daily Scan ==="
echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Scan file: $SCAN_FILE"
echo ""

# Run the scan
uv run demark --scan "$SCAN_FILE" --interval 1d --period 1y 2>&1

# Find the latest CSV
LATEST_CSV=$(ls -t "$REPORT_DIR"/scan_results_*.csv 2>/dev/null | head -1)

if [ -z "$LATEST_CSV" ] || [ ! -f "$LATEST_CSV" ]; then
    echo "No results file found. Sending empty report."
    python3 -c "
import os, requests
api_key = os.getenv('MAILGUN_API_KEY')
domain = os.getenv('MAILGUN_DOMAIN')
to_email = os.getenv('DEMARK_EMAIL_TO', 'ggoni@anticiparte.cl')
if api_key and domain:
    date = __import__('datetime').datetime.now().strftime('%Y-%m-%d')
    resp = requests.post(
        f'https://api.mailgun.net/v3/{domain}/messages',
        auth=('api', api_key),
        data={
            'from': f'DeMark Scanner <noreply@{domain}>',
            'to': to_email,
            'subject': f'DeMark Scan - {date} (No signals)',
            'html': f'<html><body><h1>DeMark Scan - {date}</h1><p>No BUY or SELL signals found.</p></body></html>'
        }
    )
    resp.raise_for_status()
    print('✓ Email sent (no signals)')
"
    exit 0
fi

# Parse CSV and send HTML email
python3 -c "
import csv, os, requests
from datetime import datetime

csv_path = '$LATEST_CSV'
api_key = os.getenv('MAILGUN_API_KEY')
domain = os.getenv('MAILGUN_DOMAIN')
to_email = os.getenv('DEMARK_EMAIL_TO', 'ggoni@anticiparte.cl')

signals = []
with open(csv_path) as f:
    reader = csv.DictReader(f)
    for row in reader:
        signals.append(row)

date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

rows_html = ''
for s in signals:
    action = s.get('Action', '')
    color = 'green' if action.startswith('BUY') else 'red'
    rows_html += f'''<tr style=\"border-bottom:1px solid #ddd;\">
        <td style=\"padding:10px;border-right:1px solid #ddd;\">{s.get('Ticker','')}</td>
        <td style=\"padding:10px;border-right:1px solid #ddd;\">{s.get('Price','')}</td>
        <td style=\"padding:10px;border-right:1px solid #ddd;\">{s.get('Support','N/A')}</td>
        <td style=\"padding:10px;border-right:1px solid #ddd;\">{s.get('Resist','N/A')}</td>
        <td style=\"padding:10px;border-right:1px solid #ddd;color:{color};font-weight:bold;\">{action}</td>
        <td style=\"padding:10px;\">{s.get('Score','')}</td></tr>'''

html = f'''<html><head><style>
body {{ font-family:Arial,sans-serif;color:#333; }}
h1 {{ color:#2c3e50; }}
table {{ border-collapse:collapse;width:100%;margin:20px 0; }}
th {{ padding:12px;text-align:left;border-right:1px solid #ccc;background-color:#f0f0f0;border-bottom:2px solid #333; }}
td {{ padding:10px; }}
</style></head><body>
<h1>DeMark Daily Scan</h1>
<p>Generated: {date} | Signals: {len(signals)}</p>
<table><thead><tr>
<th>Ticker</th><th>Price</th><th>Support</th><th>Resist</th><th>Action</th><th>Score</th>
</tr></thead><tbody>{rows_html}</tbody></table>
<p style=\"margin-top:30px;color:#7f8c8d;font-size:12px;\">Powered by DeMark Patterns engine.</p>
</body></html>'''

resp = requests.post(
    f'https://api.mailgun.net/v3/{domain}/messages',
    auth=('api', api_key),
    data={
        'from': f'DeMark Scanner <noreply@{domain}>',
        'to': to_email,
        'subject': f'DeMark Scan - {datetime.now().strftime(\"%Y-%m-%d\")} ({len(signals)} signals)',
        'html': html
    }
)
resp.raise_for_status()
print(f'✓ Email sent with {len(signals)} signals')
"