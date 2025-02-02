# User Guide

## Introduction
Registered Investment Companies (RIC) except money market funds are required to publish their portfolio holdings as well as risk and stress tests with a NPORT-P filing.
Until August 2024 these reports had to be made on a quarterly frequency with the filing of the report 30 days after the fiscal quarter-end and the publication 60 days later.
Since then its frequency has been increased to monthly reports.
The reports contain a limited set of static reference data as well as fair values for each instrument at the report date.
Therefore, they can shed some light into the current pricing in certain illiquid markets.
Also for any other data projects analyzing the movements in funds portfolios or the positioning of certain entities, the reports can be very valuable.

This package aims to build a simple connector to receive the data contained in these reports.
While other packages focussing on SEC filings have a broader range of supported filings, they lack the required detail often required for the NPORT-P filings.
In case you look for something with a more general support for SEC filings, the package [edgartools](https://github.com/dgunning/edgartools) is recommended.
Some of the bone architecture with connecting to the SEC is also heavily inspired from that project.

## Installing sec-nport
The package is distributed using the python packet manager PyPI.
This enables the easy installation using [pip](http://pypi.python.org/pypi/pip/):
<code-block lang="bash">pip install sec-nport</code-block>

## Code examples
### Setting your identity
In order to send requests to the SEC, it is required to set your identity with your email address.
This is implemented by using the environment variable `EDGAR_IDENTITY`.
A simple code example for setting your identity looks like this:
<code-block lang="python">
import os

os.environ["EDGAR_IDENTITY"] = "your-email-address@provider.com"
</code-block>
Afterwards, you can use any functions without issues.
All requests are automatically rate-limited to a maximum of 8 requests per second which is a little below the allowed 10 requests per second ensuring that you are not timed out.
Please keep in mind that the rate-limit is not designed to be threadsafe.
This is also not required since your script is almost surely faster than the rate-limit, thus giving you no advantage of using multi-threading.

### Get a list of filings
Before being able to download all filings, you first need to get a list of the available reports.
You are able to list reports for any type of form but currently this package supports only the download of NPORT-P filings.
The support may be extended in the future for other forms like N-MFP which contains the portfolio holdings of money market funds.
<code-block lang="Python">
import nport

# All NPORT-P reports with a filing date in 2023 Q1
filings = nport.get_filings(year=2023, quarter=1, form="NPORT-P")

# All reports with a filing date in the years 2022 - 2024
filings = nport.get_filings(year=[2022, 2023, 2024])
</code-block>
In the variable filings, a pandas dataframe will be loaded with the columns form, company, cik, filing_date, accession_number and url.

### Download a filing
To read the filing, there are different ways.
The easiest would be to just use the downloaded dataframe of filings and iterate over the given list of URLs.
You could also give the path to a local xml file containing the NPORT-P report.
<code-block lang="Python">
import nport

# Read NPORT-P report from URL
report = nport.NPORT.from_url("https://www.sec.gov/Archives/edgar/data/1605941/0001752724-23-071205.txt")

# Read NPORT-P report from file
path = "./0001752724-23-071205.xml"
report = nport.NPORT.from_file(path)
</code-block>
The report variable is an instance of the NPORT class and contains three main parts.
First, a Registrant instance with <code>report.registrant</code> which gives you all general information about the filing company.
Second, you find a Fund instance with <code>report.fund</code> showing you all information given about the fund itself, e.g. risk and stress tests and amount of total assets.
Last, there is a list of portfolio holdings given in <code>report.securities</code>, containing all instruments held by the fund with all the given static reference data and price information.
Since the price information is probably on of the most relevant parts for the majority of users of this library, there is an easy way to download it together with all identifiers of the security and some other relevant information like holding size and currency.
<code-block lang="Python">
prices = report.export_prices()
</code-block>