import re
import itertools
from datetime import datetime, date
import pytz
from pandas.tseries.offsets import BDay


def listify(value):
    """
    Convert the input to a list if it's not already a list.

    Args:
    value: Any type of input

    Returns:
    list: The input as a list
    """
    if isinstance(value, list):
        return value
    return [value]


def is_valid_date(date_str: str, date_format: str = "%Y-%m-%d") -> bool:
    """
    Check if the date is valid regarding the specified date format
    """
    pattern = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(pattern, date_str):
        return False
    try:
        datetime.strptime(date_str, date_format)
        return True
    except ValueError:
        return False


def is_valid_filing_date(filing_date: str) -> bool:
    """
    Check if filing_date is given in the correct format
    """
    if ":" in filing_date:
        # Check for only one colon
        if filing_date.count(":") > 1:
            return False
        start_date, end_date = filing_date.split(":")
        if start_date:
            if not is_valid_date(start_date):
                return False
        if end_date:
            if not is_valid_date(end_date):
                return False
    else:
        if not is_valid_date(filing_date):
            return False
    return True


def is_start_of_quarter():
    """
    Check if today is the first business day of the quarter
    """
    today = datetime.now().date()

    # Check if it's the start of a quarter
    if today.month in [1, 4, 7, 10] and today.day <= 5:
        # Get the first day of the current quarter
        first_day_of_quarter = datetime(today.year, today.month, 1).date()

        # Calculate one business day after the start of the quarter
        one_business_day_after = (first_day_of_quarter + BDay(1)).date()

        # Check if we haven't passed one full business day yet
        if today <= one_business_day_after:
            return True
    return False


def split_filing_date(filing_date: str) -> tuple[date, date]:
    """
    Get start and end date from filing date
    """
    if ":" in filing_date:
        start_date, end_date = filing_date.split(":")

        if not start_date:
            start_date = date(1994, 6, 1)
        else:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()

        if not end_date:
            end_date = date.today()
        else:
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    else:
        start_date = datetime.strptime(filing_date, "%Y-%m-%d").date()
        end_date = start_date

    return start_date, end_date


def filing_date_to_year_quarters(filing_date: str) -> list[tuple[int, int]]:
    """
    Build list of year and quarter combinations from timeframe in filing_date
    """
    start_date, end_date = split_filing_date(filing_date)
    start_quarter = (start_date.month - 1) // 3 + 1
    end_quarter = (end_date.month - 1) // 3 + 1

    result = []
    for year in range(start_date.year, end_date.year + 1):
        if year == start_date.year and year == end_date.year:
            quarters = range(start_quarter, end_quarter + 1)
        elif year == start_date.year:
            quarters = range(start_quarter, 5)
        elif year == end_date.year:
            quarters = range(1, end_quarter + 1)
        else:
            quarters = range(1, 5)

        for quarter in quarters:
            result.append((year, quarter))
    return result


def current_year_and_quarter() -> tuple[int, int]:
    """
    Get the year and quarter of today's date
    """
    # Define the Eastern timezone
    eastern = pytz.timezone("America/New_York")

    # Get the current time in Eastern timezone
    now_eastern = datetime.now(eastern)

    # Calculate the current year and quarter
    current_year, current_quarter = now_eastern.year, (now_eastern.month - 1) // 3 + 1
    return current_year, current_quarter


def available_quarters() -> list[tuple[int, int]]:
    """
    Get a list of year and quarter tuples
    :return:
    """
    current_year, current_quarter = current_year_and_quarter()
    start_quarters = [(1994, 3), (1994, 4)]
    in_between_quarters = list(itertools.product(range(1995, current_year), range(1, 5)))
    end_quarters = list(itertools.product([current_year], range(1, current_quarter + 1)))
    return start_quarters + in_between_quarters + end_quarters
