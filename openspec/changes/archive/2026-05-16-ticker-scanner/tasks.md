## 1. CLI Preparation

- [x] 1.1 Add `--scan` flag to `argparse` in `demark/cli.py`.
- [x] 1.2 Implement a helper function to read and parse tickers from a file (handling spaces/newlines).

## 2. Scanner Logic

- [x] 2.1 Refactor `main()` to branch between single ticker mode and scan mode.
- [x] 2.2 Implement a `run_scanner` function that iterates through tickers.
- [x] 2.3 Add `try-except` handling per ticker to skip errors and keep scanning.
- [x] 2.4 Implement logic to identify "BUY" or "SELL" signals from the latest bar.

## 3. Output & Formatting

- [x] 3.1 Create a summary table display using `pandas` or `tabulate` (or reuse current formatting) for filtered signals.
- [x] 3.2 Add color-coding to the scanner summary table for quick signal identification.

## 4. Verification

- [x] 4.1 Run the scanner against `line.txt` and verify results.
- [x] 4.2 Ensure invalid tickers are reported as warnings but don't stop the process.
