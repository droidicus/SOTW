#!/usr/bin/env python
""" This script parses the bank CSV file, calculated the commission per employee, and
    output the data to the console for human consumption
"""
import argparse

from utils import read_bank_csv, pretty_print_df

# CONSTANTS
COMMISSION_RATE = 0.3
FILENAME = "sotw.csv"


# The main thing
def main(filename, rate, end_date=None, all=False, quiet=False):
    # Read in the data
    df, start_date, end_date = read_bank_csv(filename, end_date, not all)

    # Select the purchases
    df_purchases = df[df["type"] == "purchase"]

    # Print out some data, make sure the deltas make sense!
    print(f"Commissions for the week {start_date} to {end_date} at a rate of {rate}:\n")
    print(
        f"First sale delta: {end_date - df_purchases.index[0]} - {df_purchases.index[0]}"
    )
    print(
        f"Last sale delta: {df_purchases.index[-1] - start_date} - {df_purchases.index[-1]}"
    )

    # Group by person charging, calculate commissions, print it out
    commissions = (
        (df_purchases.groupby(["requestor"]).sum()["change"] * rate)
        .round()
        .rename("Commissions")
    )
    print(commissions.sort_values(ascending=False).to_markdown())

    # Verbose output
    if not quiet:
        print_details(df)


def print_details(df):
    # Purchases
    df_purchases = df[df["type"] == "purchase"]

    # Ganja Greg and Deposits
    df_deposits = df[df["type"] == "deposit"]
    store_mask = df_deposits["comment"] == "Purchase From Store"
    df_greg = df_deposits[store_mask]
    df_deposits = df_deposits[~store_mask]

    # Transfers
    df_transfers = df[df["type"] == "transfer"]
    outgoing_mask = df_transfers["direction"] == "outgoing"
    df_outgoing_transfers = df_transfers[outgoing_mask]
    df_incoming_transfers = df_transfers[~outgoing_mask]

    # Withdrawals
    df_withdraws = df[df["type"] == "withdraw"]

    # Sums
    decompose_sum = (
        df_purchases["change"].sum()
        + df_greg["change"].sum()
        + df_deposits["change"].sum()
        + df_outgoing_transfers["change"].sum()
        + df_incoming_transfers["change"].sum()
        + df_withdraws["change"].sum()
    )
    week_sum = df["change"].sum()
    gross_profit = (
        df_purchases["change"].sum()
        + df_greg["change"].sum()
        + df_deposits["change"].sum()
        + df_incoming_transfers["change"].sum()
    )
    expenses = df_outgoing_transfers["change"].sum() + df_withdraws["change"].sum()
    net_profit = gross_profit + expenses  # - commissions.sum()

    # Check them
    if week_sum != decompose_sum:
        raise ValueError(
            "SOMETHING IS WRONG!!! Sum of all transactions not matching sum by transction types"
        )

    # Print out stats
    print("\nBalance validation passed.")
    print(f"Gross profit:\t${gross_profit:,.0f}")
    print(f"Expenses:\t${-expenses:,.0f}")
    print(f"Net profit:\t${net_profit:,.0f}")
    print(f"\nGanja Greg sales: ${df_greg['change'].sum():,.0f}")

    print("\nDeposits:")
    pretty_print_df(df_deposits)

    print("\nTransfers Out:")
    pretty_print_df(df_outgoing_transfers)

    print("\nTransfers In:")
    pretty_print_df(df_incoming_transfers)

    print("\nWithdrawals:")
    pretty_print_df(df_withdraws)


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
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process ALL data instead of only one week.",
    )
    parser.add_argument(
        "--quiet", action="store_true", help="Don't produce as much output."
    )
    args = parser.parse_args()

    # Affirm
    main(args.file, args.rate, args.end_date, args.all, args.quiet)
