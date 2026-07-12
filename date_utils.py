from datetime import datetime, timedelta

def generate_weekly_ranges(start_date, end_date):

    start = datetime.fromisoformat(
        start_date.replace("Z", "+00:00")
    )

    end = datetime.fromisoformat(
        end_date.replace("Z", "+00:00")
    )

    while start <= end:

        week_end = min(
            start + timedelta(days=6),
            end
        )

        yield (
            start.strftime("%Y-%m-%dT00:00:00.000Z"),
            week_end.strftime("%Y-%m-%dT23:59:59.999Z")
        )

        start = week_end + timedelta(days=1)

def generate_monthly_ranges(start_year, start_month, end_year, end_month):
    """
    Yields (start_date, end_date, year, month) tuples for each month
    in the given range, in the ISO format required by the Copernicus API.
    """
    year = start_year
    month = start_month

    while (year, month) <= (end_year, end_month):

        start = datetime(year, month, 1)

        if month == 12:
            next_month_start = datetime(year + 1, 1, 1)
        else:
            next_month_start = datetime(year, month + 1, 1)

        end = next_month_start - timedelta(seconds=1)

        yield (
            start.strftime("%Y-%m-%dT00:00:00.000Z"),
            end.strftime("%Y-%m-%dT23:59:59.999Z"),
            year,
            month
        )

        month += 1
        if month > 12:
            month = 1
            year += 1