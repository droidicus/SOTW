#!/usr/bin/env python
""" This script parses the bank CSV file, calculated the commission per employee, and
    output the data to the console for human consumption
"""
import argparse
from datetime import date, datetime, time, timedelta, timezone

import pandas as pd
from dateutil.relativedelta import FR, relativedelta

# CONSTANTS
COMMISSION_RATE = 0.3
FILENAME = "sotw.csv"

# The main thing
def main(filename, rate, end_date):
    # Read in the data
    df = pd.read_csv(filename)

    # Decode the 'direction' field
    df["change"] = df["change"] * (1 - 2 * (df["direction"] == "outgoing"))

    # lol... cumsum...
    df["balance"] = df.loc[::-1, "change"].cumsum()[::-1]

    # Decode the timestamp
    df["datetime"] = pd.to_datetime(df["timestamp"], utc=True)

    # Someone doesn't sanitize their inputs...
    df["requestor"] = df["requestor"].str.replace("\t", " ")
    df["requestor"] = df["requestor"].str.replace("\n", " ")

    # Index on the datetime
    df_dtindex = df.set_index("datetime")

    # Deal the end date
    if end_date is None:
        # Calculate the last friday of a full week of data
        end_date = datetime.now(timezone.utc).date() + relativedelta(weekday=FR(-1))
    else:
        # Convert from ISO format date
        end_date = date.fromisoformat(end_date)

    # Start at midnight UTC, calculate back 1 week
    end_date = datetime.combine(end_date, time(0, tzinfo=timezone.utc))
    start_date = end_date - timedelta(weeks=1)

    # Slice the week of transactions
    df_week = df_dtindex.loc[end_date:start_date]

    # Select the purchases
    df_purchases = df_week[df_week["type"] == "purchase"]

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
    help_str = (
        "End date for week, YYYY-MM-DD format. If not given, use the most recent Friday"
    )
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
