
# Personal Expense Tracker

A desktop expense tracker built with Tkinter, pandas, and numpy.

## Files
- `expense_tracker.py` — main application
- `expenses.csv` — sample data you can load to see the UI populated

## How to run
1. Ensure you have Python 3.8+ installed.
2. Install dependencies:
   ```bash
   pip install pandas numpy
   ```
3. Run the app:
   ```bash
   python expense_tracker.py
   ```

## Notes
- Dates are parsed flexibly, but prefer `YYYY-MM-DD` (e.g., `2025-08-16`).
- Use **Save CSV** to store your data anywhere you like.
- Use **Export Monthly Summary** to get a year-month rollup (with per-category columns).
