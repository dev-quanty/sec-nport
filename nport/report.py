import os.path
from pathlib import Path

from pydantic import BaseModel
from bs4 import BeautifulSoup
import pandas as pd

from nport._connector import download_text
from nport.fund import Registrant, Fund
from nport.instruments import BaseInstrument, DebtSecurity, Derivative


BASE_DIR, _ = os.path.split(__file__)


class NPORT(BaseModel):
    """
    Class of a NPORT-P Filing
    """
    registrant: Registrant
    fund: Fund
    securities: list[BaseInstrument | DebtSecurity | Derivative]

    def __repr__(self):
        return f"{self.registrant.name} [{self.registrant.report_date:%Y-%m-%d}]"

    def __str__(self):
        return self.__repr__()

    @classmethod
    def from_file(cls, path: str | Path, **kwargs):
        """
        Create NPORT class object from path to filing

        Args:
            path (str or Path):
                Path to the filing
            **kwargs:
                Additional arguments to hand over to the open function

        Returns:
            NPORT: NPORT class object
        """
        with open(path, "r", **kwargs) as file:
            xml = file.read()

        root = BeautifulSoup(xml, features="xml")
        return cls.from_xml(root)

    @classmethod
    def from_str(cls, xml: str):
        """
        Create NPORT class object from filings text

        Args:
            xml (str):
                Text of the filing

        Returns:
            NPORT: NPORT class object
        """
        root = BeautifulSoup(xml, features="xml")
        return cls.from_xml(root)

    @classmethod
    def from_url(cls, url: str):
        """
        Create NPORT class object from filings url

        Args:
            url (str):
                URL of the filing

        Returns:
            NPORT: NPORT class object
        """
        xml = download_text(url)
        return cls.from_str(xml)

    @classmethod
    def from_xml(cls, root: BeautifulSoup):
        """
        Create NPORT class object from the XML root tag

        Args:
            root (BeautifulSoup): Root of the filing

        Returns:
            NPORT: NPORT class object
        """
        form_tag = root.find("formData")

        registrant_tag = form_tag.find("genInfo")
        registrant = Registrant.from_xml(registrant_tag)

        fund_tag = form_tag.find("fundInfo")
        fund = Fund.from_xml(fund_tag)

        securities_tag = form_tag.find("invstOrSecs")
        securities = []
        for security_tag in securities_tag.find_all("invstOrSec"):
            if security_tag.find("debtSec"):
                securities.append(DebtSecurity.from_xml(security_tag, registrant.report_date))
            elif security_tag.find("derivativeInfo"):
                securities.append(Derivative.from_xml(security_tag, registrant.report_date))
            else:
                securities.append(BaseInstrument.from_xml(security_tag, registrant.report_date))

        return cls(
            registrant=registrant,
            fund=fund,
            securities=securities
        )

    def export_prices(self):
        """
        Compile the identifiers and prices for all instruments listed in the report
        """
        price_list = [security.to_list() for security in self.securities]
        return pd.DataFrame(price_list)
