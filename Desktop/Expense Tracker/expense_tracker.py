#!/usr/bin/env python3
"""
Personal Expense Tracker (Tkinter + pandas + numpy)

Features
- Add expenses with Date, Category, Amount, Description
- View expenses in a table (ttk.Treeview)
- Delete selected rows
- Load from / Save to CSV
- Filter by date range and/or category
- Live total and per-category totals
- Export monthly summary CSV (Year-Month, Total, and per-category breakdown)

Dependencies: Python 3.8+, pandas, numpy (Tkinter is in the stdlib)
Run: python expense_tracker.py
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
from datetime import date, datetime

APP_TITLE = "Personal Expense Tracker"
DEFAULT_COLUMNS = ["Date", "Category", "Amount", "Description"]
DEFAULT_CATEGORIES = [
    "Food", "Transport", "Bills", "Shopping", "Entertainment",
    "Health", "Education", "Groceries", "Travel", "Other"
]
DEFAULT_CSV = "expenses.csv"
DATE_FMT = "%Y-%m-%d"  # ISO format

def parse_date(s: str):
    s = s.strip()
    if not s:
        return None
    # Try ISO first
    fmts = ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d", "%d %b %Y", "%d %B %Y"]
    for f in fmts:
        try:
            return datetime.strptime(s, f).date()
        except ValueError:
            continue
    raise ValueError("Invalid date format. Try YYYY-MM-DD (e.g., 2025-08-16).")

class ExpenseTracker(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("980x640")
        self.minsize(900, 600)

        # Data
        self.df = pd.DataFrame(columns=DEFAULT_COLUMNS)
        self.current_path = os.path.abspath(DEFAULT_CSV)  # default save path
        self.filtered_df = None  # cache of filtered view

        self._build_ui()

        # Try loading default CSV if present
        if os.path.exists(self.current_path):
            try:
                self.load_csv(self.current_path)
            except Exception as e:
                messagebox.showwarning("Load Warning", f"Could not load default CSV:\n{e}")
        else:
            # Start with today's row suggestion (not added automatically)
            pass

        self.refresh_table()

    # ---------------- UI ----------------
    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Top form frame
        form = ttk.LabelFrame(self, text="Add Expense")
        form.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 6))
        for i in range(12):
            form.columnconfigure(i, weight=1)

        # Date
        ttk.Label(form, text="Date (YYYY-MM-DD)").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        self.date_var = tk.StringVar(value=date.today().strftime(DATE_FMT))
        self.date_entry = ttk.Entry(form, textvariable=self.date_var, width=16)
        self.date_entry.grid(row=0, column=1, padx=6, pady=6, sticky="w")

        # Category
        ttk.Label(form, text="Category").grid(row=0, column=2, padx=6, pady=6, sticky="w")
        self.category_var = tk.StringVar(value=DEFAULT_CATEGORIES[0])
        self.category_menu = ttk.Combobox(form, textvariable=self.category_var, values=DEFAULT_CATEGORIES, state="readonly", width=18)
        self.category_menu.grid(row=0, column=3, padx=6, pady=6, sticky="w")

        # Amount
        ttk.Label(form, text="Amount").grid(row=0, column=4, padx=6, pady=6, sticky="w")
        self.amount_var = tk.StringVar()
        self.amount_entry = ttk.Entry(form, textvariable=self.amount_var, width=12)
        self.amount_entry.grid(row=0, column=5, padx=6, pady=6, sticky="w")

        # Description
        ttk.Label(form, text="Description").grid(row=0, column=6, padx=6, pady=6, sticky="w")
        self.desc_var = tk.StringVar()
        self.desc_entry = ttk.Entry(form, textvariable=self.desc_var, width=40)
        self.desc_entry.grid(row=0, column=7, columnspan=2, padx=6, pady=6, sticky="ew")

        # Add button
        self.add_btn = ttk.Button(form, text="Add", command=self.on_add)
        self.add_btn.grid(row=0, column=9, padx=6, pady=6, sticky="e")

        # Filter frame
        filt = ttk.LabelFrame(self, text="Filter")
        filt.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 6))
        for i in range(10):
            filt.columnconfigure(i, weight=1)

        ttk.Label(filt, text="From").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        self.from_var = tk.StringVar()
        ttk.Entry(filt, textvariable=self.from_var, width=14).grid(row=0, column=1, padx=6, pady=6, sticky="w")

        ttk.Label(filt, text="To").grid(row=0, column=2, padx=6, pady=6, sticky="w")
        self.to_var = tk.StringVar()
        ttk.Entry(filt, textvariable=self.to_var, width=14).grid(row=0, column=3, padx=6, pady=6, sticky="w")

        ttk.Label(filt, text="Category").grid(row=0, column=4, padx=6, pady=6, sticky="w")
        self.filter_cat_var = tk.StringVar(value="All")
        cat_values = ["All"] + DEFAULT_CATEGORIES
        ttk.Combobox(filt, textvariable=self.filter_cat_var, values=cat_values, state="readonly", width=18).grid(row=0, column=5, padx=6, pady=6, sticky="w")

        ttk.Button(filt, text="Apply Filter", command=self.apply_filter).grid(row=0, column=6, padx=6, pady=6, sticky="w")
        ttk.Button(filt, text="Clear Filter", command=self.clear_filter).grid(row=0, column=7, padx=6, pady=6, sticky="w")

        # Table frame
        table_frame = ttk.Frame(self)
        table_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 6))
        self.rowconfigure(2, weight=1)

        self.tree = ttk.Treeview(table_frame, columns=DEFAULT_COLUMNS, show="headings", selectmode="extended")
        for col in DEFAULT_COLUMNS:
            self.tree.heading(col, text=col)
            anchor = "e" if col == "Amount" else "w"
            width = 120 if col in ("Date", "Category") else (100 if col == "Amount" else 420)
            self.tree.column(col, anchor=anchor, width=width, stretch=True)
        self.tree.pack(side="left", fill="both", expand=True)

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=vsb.set)

        # Bottom bar
        bottom = ttk.Frame(self)
        bottom.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))
        for i in range(10):
            bottom.columnconfigure(i, weight=1)

        ttk.Button(bottom, text="Delete Selected", command=self.on_delete).grid(row=0, column=0, padx=6, pady=6, sticky="w")
        ttk.Button(bottom, text="Load CSV", command=self.on_load_csv).grid(row=0, column=1, padx=6, pady=6, sticky="w")
        ttk.Button(bottom, text="Save CSV", command=self.on_save_csv).grid(row=0, column=2, padx=6, pady=6, sticky="w")
        ttk.Button(bottom, text="Export Monthly Summary", command=self.on_export_summary).grid(row=0, column=3, padx=6, pady=6, sticky="w")

        # totals
        self.total_var = tk.StringVar(value="Total: 0.00")
        ttk.Label(bottom, textvariable=self.total_var, font=("", 10, "bold")).grid(row=0, column=5, padx=6, pady=6, sticky="e")

        self.cat_total_var = tk.StringVar(value="By Category: —")
        ttk.Label(bottom, textvariable=self.cat_total_var).grid(row=0, column=6, columnspan=3, padx=6, pady=6, sticky="e")

        # Style tweaks
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")

    # ------------- Data helpers -------------
    def get_view_df(self):
        """Return the DataFrame currently displayed (filtered or full)."""
        return self.filtered_df if self.filtered_df is not None else self.df

    def refresh_table(self):
        # Clear
        for i in self.tree.get_children():
            self.tree.delete(i)

        view = self.get_view_df()
        # Insert rows
        for _, row in view.iterrows():
            values = [row["Date"], row["Category"], f"{row['Amount']:.2f}", row["Description"]]
            self.tree.insert("", "end", values=values)

        # Update totals
        amounts = pd.to_numeric(view["Amount"], errors="coerce").fillna(0.0).to_numpy()
        total = float(np.nansum(amounts)) if amounts.size else 0.0
        self.total_var.set(f"Total: {total:.2f}")

        # Per-category
        if not view.empty:
            per_cat = view.groupby("Category")["Amount"].sum().sort_values(ascending=False)
            snippet = ", ".join([f"{k}: {v:.2f}" for k, v in per_cat.items()])
            self.cat_total_var.set(f"By Category: {snippet}")
        else:
            self.cat_total_var.set("By Category: —")

    def apply_filter(self):
        try:
            df = self.df.copy()
            f = self.from_var.get().strip()
            t = self.to_var.get().strip()
            c = self.filter_cat_var.get()

            if f:
                fdate = parse_date(f)
                df = df[pd.to_datetime(df["Date"]).dt.date >= fdate]
            if t:
                tdate = parse_date(t)
                df = df[pd.to_datetime(df["Date"]).dt.date <= tdate]
            if c and c != "All":
                df = df[df["Category"] == c]

            self.filtered_df = df
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Filter Error", str(e))

    def clear_filter(self):
        self.from_var.set("")
        self.to_var.set("")
        self.filter_cat_var.set("All")
        self.filtered_df = None
        self.refresh_table()

    # ------------- Actions -------------
    def on_add(self):
        try:
            d = parse_date(self.date_var.get())
            if d is None:
                d = date.today()
            cat = self.category_var.get().strip() or "Other"

            amt_str = self.amount_var.get().strip()
            if not amt_str:
                raise ValueError("Amount is required.")
            amt = float(amt_str)
            if not np.isfinite(amt):
                raise ValueError("Amount must be a finite number.")

            desc = self.desc_var.get().strip()

            new_row = {
                "Date": d.strftime(DATE_FMT),
                "Category": cat,
                "Amount": amt,
                "Description": desc,
            }
            self.df = pd.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)

            # Clear amount & description for quick entry
            self.amount_var.set("")
            self.desc_var.set("")

            # If a filter is active, refresh view based on it
            if self.filtered_df is not None:
                self.apply_filter()
            else:
                self.refresh_table()
        except Exception as e:
            messagebox.showerror("Add Error", str(e))

    def on_delete(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Delete", "No rows selected.")
            return
        if not messagebox.askyesno("Confirm Delete", f"Delete {len(sel)} selected row(s)?"):
            return

        # Build a dataframe representing the current view, drop matching rows by position, map back to self.df
        view = self.get_view_df().reset_index(drop=True)
        indices_to_drop = []
        for item in sel:
            vals = self.tree.item(item, "values")
            # Find first matching row in view
            mask = (
                (view["Date"] == vals[0]) &
                (view["Category"] == vals[1]) &
                (view["Amount"].astype(float).round(2) == float(vals[2])) &
                (view["Description"] == vals[3])
            )
            idx = np.where(mask.to_numpy())[0]
            if idx.size:
                indices_to_drop.append(idx[0])

        if indices_to_drop:
            view = view.drop(indices_to_drop).reset_index(drop=True)
            # Now rebuild self.df depending on filter state
            if self.filtered_df is not None:
                # Remove the same rows from the original df by matching all fields (safer than index)
                to_remove = self.get_view_df().iloc[indices_to_drop]
                self.df = self.df.merge(to_remove.assign(_rm=1), how="left", indicator=False, on=DEFAULT_COLUMNS)
                self.df = self.df[self.df["_rm"].isna()].drop(columns=["_rm"])
            else:
                self.df = view

            self.clear_filter()  # clears & refreshes
        else:
            messagebox.showwarning("Delete", "Could not locate the selected rows. Try clearing filters and retry.")

    def on_load_csv(self):
        path = filedialog.askopenfilename(
            title="Load Expenses CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            self.load_csv(path)
            self.current_path = path
            self.clear_filter()
        except Exception as e:
            messagebox.showerror("Load Error", str(e))

    def load_csv(self, path: str):
        df = pd.read_csv(path)
        # Normalize columns
        missing = [c for c in DEFAULT_COLUMNS if c not in df.columns]
        if missing:
            raise ValueError(f"CSV missing columns: {missing}")
        # Ensure dtypes
        df = df[DEFAULT_COLUMNS].copy()
        # Coerce date to string ISO
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.strftime(DATE_FMT)
        # Amount numeric
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0.0)
        df["Description"] = df["Description"].fillna("").astype(str)
        df["Category"] = df["Category"].fillna("Other").astype(str)
        self.df = df

    def on_save_csv(self):
        # Offer "Save As"
        path = filedialog.asksaveasfilename(
            title="Save Expenses CSV",
            defaultextension=".csv",
            initialfile=os.path.basename(self.current_path) if self.current_path else "expenses.csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            self.save_csv(path)
            self.current_path = path
            messagebox.showinfo("Saved", f"Saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def save_csv(self, path: str):
        self.df.to_csv(path, index=False)

    def on_export_summary(self):
        if self.df.empty:
            messagebox.showinfo("Export Summary", "No data to summarize.")
            return

        try:
            df = self.df.copy()
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            df = df.dropna(subset=["Date"])
            df["YearMonth"] = df["Date"].dt.to_period("M").astype(str)

            # Total per month
            totals = df.groupby("YearMonth")["Amount"].sum().rename("Total")

            # Per-category pivot
            pivot = df.pivot_table(index="YearMonth", columns="Category", values="Amount", aggfunc="sum").fillna(0.0)

            out = pd.concat([totals, pivot], axis=1).reset_index()

            path = filedialog.asksaveasfilename(
                title="Export Monthly Summary CSV",
                defaultextension=".csv",
                initialfile="monthly_summary.csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            )
            if not path:
                return

            out.to_csv(path, index=False)
            messagebox.showinfo("Exported", f"Monthly summary exported to:\n{path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

def main():
    app = ExpenseTracker()
    app.mainloop()

if __name__ == "__main__":
    main()
