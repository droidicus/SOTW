#!/usr/bin/env python
""" This script parses the bank CSV file, calculated the commission per employee, and
    output the data to the console for human consumption
"""
import argparse
from datetime import date, datetime, time, timedelta, timezone

import pandas as pd
from dateutil.relativedelta import FR, relativedelta

from utils import read_bank_csv

# CONSTANTS
COMMISSION_RATE = 0.3
FILENAME = "sotw.csv"


# The main thing
def main(filename, rate, end_date=None):
    # Read in the data
    df, start_date, end_date = read_bank_csv(filename, end_date)

    # Select the purchases
    df_purchases = df[df["type"] == "purchase"]

    # Print out some data, make sure the deltas make sense!
    print(f"Commissions for the week {start_date} to {end_date} at a rate of {rate}")
    print(
        f"First sale delta: {end_date - df_purchases.index[0]} - {df_purchases.index[0]}"
    )
    print(
        f"Last sale delta: {df_purchases.index[-1] - start_date} - {df_purchases.index[-1]}"
    )

    # Group by person charging, calculate commissions, print it out
    commissions = (df_purchases.groupby(["requestor"]).sum()["change"] * rate).round()
    print(commissions.sort_values(ascending=False))


# Are you prepared?
if __name__ == "__main__":
    # Performing diagnostics
    parser = argparse.ArgumentParser(
        description="Simple utility to calculate commissions from a bank CSV export.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    help_str = "End date for week, YYYY-MM-DD (ISO) format. If not given, use the most recent Friday"
    parser.add_argument("--end_date", type=str, default=None, help=help_str)
    parser.add_argument(
        "--file", type=str, default=FILENAME, help="CSV bank export file to analyze."
    )
    parser.add_argument(
        "--rate", type=float, default=COMMISSION_RATE, help="Sales commission rate."
    )
    args = parser.parse_args()

    # Affirm
    main(args.file, args.rate, args.end_date)
