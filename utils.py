import pandas as pd
from datetime import date, datetime, time, timedelta, timezone
from dateutil.relativedelta import relativedelta, FR


def read_bank_csv(filename, end_date=None, slice_week=True):
    # Read in the data
    df = pd.read_csv(filename)

    # Decode the 'direction' field
    df["change"] = df["change"] * (1 - 2 * (df["direction"] == "outgoing"))

    # Decode the timestamp
    df["datetime"] = pd.to_datetime(df["timestamp"], utc=True)

    # Someone doesn't sanitize their inputs...
    df["requestor"] = df["requestor"].str.replace("\t", " ")
    df["requestor"] = df["requestor"].str.replace("\n", " ")

    # Index on the datetime
    df = df.set_index("datetime")

    if slice_week:
        # Deal with the end date
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
        df = df.loc[end_date:start_date]
    else:
        # Start and end at bounds of timestamps
        end_date = df.index.max()
        start_date = df.index.min()

    # lol... cumsum... (reversed)
    df["balance"] = df["change"][::-1].cumsum()[::-1]

    # Return dataframe
    return df, start_date, end_date


def pretty_print_df(df):
    df = df[["change", "comment", "requestor"]]
    print(df.to_markdown())


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
