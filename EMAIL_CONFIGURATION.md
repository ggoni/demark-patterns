# DeMark Email Results Configuration

## Summary

The DeMark scanner cron job has been updated to send results via **email** instead of Discord. The email will be sent to `ggoni@anticiparte.cl` with a beautifully formatted HTML table containing all BUY/SELL signals.

## Files Created

### 1. `send_email_results.py`
Main script that:
- Loads tickers from a file (default: `line.txt`)
- Runs the DeMark scanner on all tickers
- Collects all BUY/SELL signals with scores
- Formats results as an HTML table
- Sends email via Mailgun API

**Key features:**
- Automatic environment variable support:
  - `DEMARK_SCANNER_FILE`: Path to scanner file (default: `line.txt`)
  - `DEMARK_EMAIL_TO`: Email recipient (default: `ggoni@anticiparte.cl`)
  - `DEMARK_INTERVAL`: Data interval (default: `1d`)
  - `DEMARK_PERIOD`: Data period (default: `1y`)
- Mailgun credentials loaded from `~/.hermes/.env`:
  - `MAILGUN_API_KEY`
  - `MAILGUN_DOMAIN`

### 2. `test_email.py`
Test script for validating email functionality without running a full scan. Use for quick testing:
```bash
python test_email.py
```

### 3. `run_with_email.sh`
Wrapper bash script that:
1. Activates the virtual environment
2. Syncs dependencies with `uv sync`
3. Executes `send_email_results.py`

## Updated Dependencies

Added `requests>=2.31.0` to `pyproject.toml` for Mailgun API integration.

## Cron Job Configuration

The existing cron job `"Daily Demark Run"` has been updated:
- **Schedule**: `0 5 * * 1-5` (5 AM, Monday-Friday)
- **Delivery**: Changed from `discord` to `local` (email via Mailgun)
- **Script**: Uses the new `run_with_email.sh` wrapper

## Email Format

The email includes:
- **Subject**: `DeMark Scanner Results - YYYY-MM-DD (X signals)`
- **HTML Table** with columns:
  - **Ticker**: Stock symbol
  - **Price**: Current price
  - **Support**: TDST support level
  - **Resist**: TDST resistance level
  - **Action**: BUY/SELL signal (color-coded green/red)
  - **Score**: Combined importance score

Example styling:
- Green text for BUY signals
- Red text for SELL signals
- Professional HTML layout with borders and spacing

## Testing

Verified functionality with `test_email.py`:
✓ Email successfully sent to ggoni@anticiparte.cl
✓ HTML table formatting working correctly
✓ Mailgun API integration confirmed

## Usage

### Manual execution:
```bash
cd ~/prototipos/demark-patterns
./run_with_email.sh
```

### With custom parameters:
```bash
export DEMARK_SCANNER_FILE="line.txt"
export DEMARK_EMAIL_TO="ggoni@anticiparte.cl"
python send_email_results.py
```

### Testing email only (without full scan):
```bash
python test_email.py
```

## Mailgun Setup Reference

The implementation uses the Mailgun REST API v3:
- **Endpoint**: `https://api.mailgun.net/v3/{domain}/messages`
- **Auth**: Basic auth with `api` username and API key
- **From**: `noreply@{mailgun-domain}`
- **To**: Configured via environment variable or hardcoded in code

See: https://documentation.mailgun.com/docs/mailgun/api-reference/

## Notes

- The script gracefully handles cases with no signals found
- Signals are sorted by combined importance score (highest first)
- Each cron execution will generate one email with the day's results
- Results are not saved to CSV by default (configurable in code)
- The wrapper script uses `set -e` to fail fast on errors
