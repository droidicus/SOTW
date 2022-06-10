#!/usr/bin/env python
""" This script parses the bank CSV file, calculated the commission per employee, and
    output the data to the console for human consumption
"""
import argparse

import pandas as pd
import matplotlib.pyplot as plt

from utils import read_bank_csv, pretty_print_df


# CONSTANTS
COMMISSION_RATE = 0.3
FILENAME = "sotw.csv"


# The main thing
def main(filename, rate, end_date=None, slice_weeks=1, quiet=False, do_plots=False):
    # Read in the data
    df, start_date, end_date = read_bank_csv(filename, end_date, slice_weeks)

    # Select the purchases
    df_purchases = df[df["type"] == "purchase"]
    df_purchases = df_purchases[df_purchases["comment"] != "Purchase From Store"]

    # Print out some data, make sure the deltas make sense!
    print(
        f"Commissions for the week {start_date.strftime('%Y-%m-%d %H:%M:%S')} to {end_date.strftime('%Y-%m-%d %H:%M:%S')} at a rate of {rate}:\n"
    )
    print(
        f"First sale delta: {df_purchases.index[-1] - start_date} - {df_purchases.index[-1].strftime('%Y-%m-%d %H:%M:%S')}"
    )
    print(
        f"Last sale delta: {end_date - df_purchases.index[0]} - {df_purchases.index[0].strftime('%Y-%m-%d %H:%M:%S')}"
    )
    print(f"Total delta: {df_purchases.index[0] - df_purchases.index[-1]}\n")

    # Group by person charging, calculate commissions, print it out
    commissions = (
        (df_purchases.groupby(["requestor"]).sum()["change"] * rate)
        .round()
        .rename("Commissions")
    )
    print(commissions.sort_values(ascending=False).to_markdown())

    # Verbose output
    if not quiet:
        print_details(df, do_plots)


def print_details(df, do_plots=False):
    # Purchases
    df_purchases = df[df["type"] == "purchase"]
    store_mask = df_purchases["comment"] == "Purchase From Store"
    df_greg_purchases = df_purchases[store_mask]
    df_purchases = df_purchases[~store_mask]

    # Deposits
    df_deposits = df[df["type"] == "deposit"]
    store_mask = df_deposits["comment"] == "Purchase From Store"
    df_greg_deposits = df_deposits[store_mask]
    df_deposits = df_deposits[~store_mask]

    # Ganja Greg
    df_greg = pd.concat([df_greg_purchases, df_greg_deposits]).sort_index()

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

    # Check them
    if week_sum != decompose_sum:
        raise RuntimeError(
            "SOMETHING IS WRONG!!! Sum of all transactions not matching sum by transaction types"
        )

    # Did we make any money?
    gross_profit = (
        df_purchases["change"].sum()
        + df_greg["change"].sum()
        + df_deposits["change"].sum()
        + df_incoming_transfers["change"].sum()
    )
    expenses = df_outgoing_transfers["change"].sum() + df_withdraws["change"].sum()
    net_profit = gross_profit + expenses

    # Print out stats
    print(f"\nGanja Greg sales: ${df_greg['change'].sum():,.0f}")
    print("\nBalance validation passed!")
    print(f"Gross profit:\t${gross_profit:,.0f}")
    print(f"Expenses:\t${-expenses:,.0f}")
    print(f"Net profit:\t${net_profit:,.0f}")

    print("\nDeposits:")
    pretty_print_df(df_deposits)

    print("\nTransfers Out:")
    pretty_print_df(df_outgoing_transfers)

    print("\nTransfers In:")
    pretty_print_df(df_incoming_transfers)

    print("\nWithdrawals:")
    pretty_print_df(df_withdraws)

    if do_plots:
        # Delta balance over the time slice
        df.plot(y="balance", title="Delta Bank Balance").figure.savefig(
            "delta_balance.png", dpi=300
        )

        # Sales totals per hour of the day
        purchases_hr = (
            df_purchases.groupby(df_purchases.index.hour)
            .sum()[["change"]]
            .rename(columns={"change": "humans"})
        )
        greg_hr = (
            df_greg.groupby(df_greg.index.hour)
            .sum()[["change"]]
            .rename(columns={"change": "greg"})
        )
        combined_hr = (
            pd.concat([purchases_hr, greg_hr], axis=1)
            .fillna(0)
            .sort_index()
            .rename_axis("Hour Of Day (LS)")
        )
        combined_hr.index = (combined_hr.index - 6) % 24
        combined_hr = combined_hr.sort_index()
        ax = combined_hr.plot(
            title="Sales Totals by Hour of the Day", ylabel="Sales totals ($)"
        )
        plt.axvline(12, color="black", linestyle="--")
        ax.figure.savefig("sales_per_hr.png", dpi=300)

        # Sales totals per day of week
        purchases_day = (
            df_purchases.groupby(df_purchases.index.dayofweek)
            .sum()[["change"]]
            .rename(columns={"change": "humans"})
        )
        greg_day = (
            df_greg.groupby(df_greg.index.dayofweek)
            .sum()[["change"]]
            .rename(columns={"change": "greg"})
        )
        combined_day = (
            pd.concat([purchases_day, greg_day], axis=1).fillna(0).sort_index()
        )
        combined_day["Day of Week"] = ["Fri", "Sat", "Sun", "Mon", "Tues", "Wed", "Thu"]
        combined_day = combined_day.set_index("Day of Week")
        combined_day.plot(
            title="Sales Totals by Day of the Week", ylabel="Sales totals ($)"
        ).figure.savefig("sales_per_day.png", dpi=300)


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
    # parser.add_argument(
    #     "--all",
    #     action="store_true",
    #     help="Process ALL data instead of only one week.",
    # )
    parser.add_argument(
        "--weeks",
        type=int,
        default=1,
        help="Number of weeks to slice from the data, -1 for all data",
    )
    parser.add_argument(
        "--quiet", action="store_true", help="Don't produce as much output."
    )
    parser.add_argument("--plot", action="store_true", help="Make plots of stuff.")
    args = parser.parse_args()

    # Affirm
    main(args.file, args.rate, args.end_date, args.weeks, args.quiet, args.plot)
