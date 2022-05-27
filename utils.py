import pandas as pd
from datetime import date, datetime, time, timedelta, timezone
from dateutil.relativedelta import relativedelta, FR


def read_bank_csv(filename, end_date=None, slice_weeks=1):
    """Reads LS Bank CSV file and process into a reasonably formatted dataframe.

    Args:
        filename (str): File to decode.
        end_date (None, str): If None (default) picks end date that is the most recent
                              Friday at Midnight UTC. If string, it is expected to be
                              formatted in ISO format (YYYY-MM-DD).
        slice_weeks (int): Will slice off that number of weeks from the dataframe.
                           Default = 1, if value is negative e.g. `-1` all data will be used

    Returns:
        df (dataframe), start_date (datetime), end_date (datetime)): The data and start/end
    """
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

    if slice_weeks < 0:
        # Start and end at bounds of timestamps
        end_date = df.index.max()
        start_date = df.index.min()
    else:
        # Deal with the end date
        if end_date is None:
            # Calculate the last friday of a full week of data
            end_date = datetime.now(timezone.utc).date() + relativedelta(weekday=FR(-1))
        else:
            # Convert from ISO format date
            end_date = date.fromisoformat(end_date)

        # Start at midnight UTC, calculate start date from delta
        end_date = datetime.combine(end_date, time(0, tzinfo=timezone.utc))
        start_date = end_date - timedelta(weeks=slice_weeks)

        # Slice the week of transactions
        df = df.loc[end_date:start_date]

    # lol... cumsum... (reversed)
    df["balance"] = df["change"][::-1].cumsum()[::-1]

    # Return dataframe and bounds
    return df, start_date, end_date


def pretty_print_df(df):
    df = df[["change", "comment", "requestor"]]
    print(df.to_markdown())
