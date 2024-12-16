import itertools
from typing import Optional, Union, Iterable
from datetime import datetime
import logging
from rich.logging import RichHandler

import pandas as pd
import httpx

from nport._utils import (
    is_valid_filing_date, is_start_of_quarter, filing_date_to_year_quarters,
    current_year_and_quarter, available_quarters, split_filing_date, listify
)
from nport._connector import download_text


index_url = "https://www.sec.gov/Archives/edgar/full-index/{}/QTR{}/{}.{}"
form_specs: list[tuple] = [
    ("form", (0, 12), str),
    ("company", (12, 74), str),
    ("cik", (74, 82), int),
    ("filing_date", (85, 97), str),
    ("accession_number", (97, 141), str)
]
company_specs: list[tuple] = [
    ("company", (0, 62), str),
    ("form", (62, 74), str),
    ("cik", (74, 82), int),
    ("filing_date", (85, 97), str),
    ("accession_number", (97, 141), str)
]
xbrl_specs: list[tuple] = [
    ("cik", 0, int),
    ("company", 1, str),
    ("form", 2, str),
    ("filing_date", 3, str),
    ("accession_number", 4, str)
]

logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)


def read_index_table(index_text: str, index: str) -> pd.DataFrame:
    """
    Read filing index text content into pandas Dataframe
    """
    lines = index_text.rstrip("\n").split("\n")

    # Find where the data starts
    data_start = 0
    for i, line in enumerate(lines):
        if line.startswith("-----"):
            data_start = i + 1
            break

    data = []
    data_lines = lines[data_start:]

    if index.lower() == "xbrl":
        for line in data_lines:
            cells = line.split("|")
            data.append({spec[0]: spec[2](cells[spec[1]]) for spec in xbrl_specs})
    else:
        index_specs = form_specs if index.lower() == "form" else company_specs
        for line in data_lines:
            data.append({spec[0]: spec[2](line[spec[1][0]:spec[1][1]].strip()) for spec in index_specs})
    data_df = pd.DataFrame(data)
    data_df["filing_date"] = pd.to_datetime(data_df["filing_date"], format="%Y-%m-%d")
    data_df["accession_number"] = data_df["accession_number"].str.rsplit("/", expand=False).str[-1]
    data_df["accession_number"] = data_df["accession_number"].str.slice(0, -4)
    return data_df


def fetch_filing_index(year: int, quarter: int, index: str) -> pd.DataFrame | None:
    """
    Download filing index for a specified year and quarter
    """
    url = index_url.format(year, quarter, index, "gz")
    try:
        index_text = download_text(url)
        index_table = read_index_table(index_text, index)
        return index_table
    except httpx.HTTPStatusError as e:
        if is_start_of_quarter() and e.response.status_code == 403:
            logging.info(f"No filings for {year} Q{quarter} since start of new quarter.")
            return None
        logging.error(str(e))
        raise


def get_filings_for_quarters(years_and_quarters: list[tuple[int, int]], index: str
                             ) -> pd.DataFrame | None:
    """
    Fetch the filings for all year, quarter combinations
    """
    filings = []
    for year, quarter in years_and_quarters:
        filings_quarter = fetch_filing_index(year, quarter, index)
        if filings_quarter is not None:
            filings.append(filings_quarter)
    filings = pd.concat(filings)
    return filings


def get_filings(
        year: Optional[int | list[int]] = None,
        quarter: Optional[int | list[int]] = None,
        form: Optional[Union[str, list[str]]] = None,
        filing_date: Optional[str] = None,
        index="form"
) -> pd.DataFrame:
    """
    Downloads the filing index from Edgar and filters by year, quarter, filing_date or form.

    Args:
        year (int or Iterable, optional):
            The year or list of years of the filings, e.g. 2024.
        quarter (int or Iterable, optional):
            The quarter or list of quarters of the filing, e.g. 4 for the forth quarter.
        form (str or Iterable, optional):
            The form or forms of the filing, e.g. "NPORT-P" or ["NPORT-P", "10-K"].
        filing_date (str, optional):
            The filing date to filter by given as single day (YYYY-MM-DD) or a range
            of days (YYYY-MM-DD:YYYY-MM-DD).
        index (str, optional):
            The index type - "form" or "company" or "xbrl". Defaults to "form".

    Returns:
        pd.DataFrame: Dataframe of the queried filings
    """
    if filing_date:
        if not is_valid_filing_date(filing_date):
            logging.warning(
                "Provide a valid filing date in the format YYYY-MM-DD or YYYY-MM-DD:YYYY-MM-DD"
            )
            return pd.DataFrame([])
        year_and_quarters = filing_date_to_year_quarters(filing_date)
    elif not year:
        year, quarter = current_year_and_quarter()
        year_and_quarters = [(year, quarter)]
    else:
        year = listify(year)
        if quarter is None:
            quarter = [1, 2, 3, 4]
        else:
            quarter = listify(quarter)
        available_yq = available_quarters()
        year_and_quarters = [yq for yq in itertools.product(year, quarter) if yq in available_yq]

    if len(year_and_quarters) == 0:
        logging.warning(f"""
Provide a year between 1994 and {datetime.now().year} and optionally a quarter (1-4) for which
the SEC has filings.

    e.g. filings = get_filings(2023) OR
         filings = get_filings(2023, 1)

(You specified the year {year} and quarter {quarter})
        """)
        return pd.DataFrame([])
    filings = get_filings_for_quarters(year_and_quarters, index=index)

    if isinstance(form, str):
        filings = filings.loc[filings["form"] == form.upper()]
    elif isinstance(form, Iterable):
        filings = filings.loc[filings["form"].isin(form)]

    if filing_date:
        start_date, end_date = split_filing_date(filing_date)
        filings = filings.loc[
            (filings["filing_date"] >= start_date) & (filings["filing_date"] <= end_date)
            ]

    filings["url"] = ("https://www.sec.gov/Archives/edgar/data/" + filings["cik"].astype(str) + "/"
                      + filings["accession_number"] + ".txt")
    return filings
