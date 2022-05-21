#!/usr/bin/env python
""" This script parses the bank CSV file, calculated the commission per employee, and
    output the data to the console for human consumption
"""
import argparse
from datetime import datetime, time, timedelta

import pandas as pd
import seaborn as sns
from dateutil.relativedelta import FR, relativedelta

# CONSTANTS
COMMISSION_RATE = 0.3
FILENAME = "sotw.csv"

# The main thing
def main(filename, rate):
    # Read in the data
    df = pd.read_csv(filename)

    # Decode the 'direction' field
    df["change"] = df["change"] * (1 - 2 * (df["direction"] == "outgoing"))

    # lol... cumsum...
    df["balance"] = df.loc[::-1, "change"].cumsum()[::-1]

    # Decode the timestamp
    df["datetime"] = pd.to_datetime(df["timestamp"])

    # Someone doesn't sanitize their inputs...
    df["requestor"] = df["requestor"].str.replace("\t", " ")
    df["requestor"] = df["requestor"].str.replace("\n", " ")

    # Index on the datetime
    df_dtindex = df.set_index("datetime")

    # Calculate the last friday of a full week of data
    last_friday = datetime.now().date() + relativedelta(weekday=FR(-1))
    last_friday = datetime.combine(last_friday, time(0))

    # Slice the week of transactions
    df_week = df_dtindex.loc[last_friday : last_friday - timedelta(weeks=1)]

    # Select the purchases
    df_purchases = df_week[df_week["type"] == "purchase"]

    # Group by person charging, calculate commissions, print it out
    commissions = (df_purchases.groupby(["requestor"]).sum()["change"] * rate).round()
    print(commissions)


# Are you prepared?
if __name__ == "__main__":
    # Performing diagnostics
    parser = argparse.ArgumentParser(
        description="Simple utility to calculate commissions from a bank CSV export.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--file", type=str, default=FILENAME, help="CSV bank export file to analyze."
    )
    parser.add_argument(
        "--rate", type=float, default=COMMISSION_RATE, help="Sales commission rate."
    )
    args = parser.parse_args()

    # Affirm
    main(args.file, args.rate)
