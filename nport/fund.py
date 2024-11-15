from typing import Optional
from datetime import date
from pydantic import BaseModel
from nport.xmltools import find_element, child_text, optional_decimal_text, optional_decimal_value


class Registrant(BaseModel):
    # Elements of A.1
    name: str
    file_number: str
    cik: int
    lei: str
    street_address1: str
    street_address2: Optional[str]
    city: str
    state: Optional[str]
    country: Optional[str]
    zip_code: int
    telephone: str

    # Elements of A.2
    series_name: str
    series_edgar_identifier: str
    series_lei: str

    # Elements of A.3 and A.4
    fiscal_year_end: date
    report_date: date
    is_final_filing: bool


class PortfolioInterestRisk(BaseModel):
    # Elements of B.3.a and B.3.b
    currency: str
    dv01_3m: float
    dv01_1y: float
    dv01_5y: float
    dv01_10y: float
    dv01_30y: float
    dv100_3m: float
    dv100_1y: float
    dv100_5y: float
    dv100_10y: float
    dv100_30y: float


class PortfolioCreditRisk(BaseModel):
    # Elements of B.3.c
    cs01_3m_ig: float
    cs01_1y_ig: float
    cs01_5y_ig: float
    cs01_10y_ig: float
    cs01_30y_ig: float
    cs01_3m_junk: float
    cs01_1y_junk: float
    cs01_5y_junk: float
    cs01_10y_junk: float
    cs01_30y_junk: float


class Borrower(BaseModel):
    # Elements of B.4.a
    name: str
    lei: Optional[str]
    aggregate_value: float


class NonCashCollateral(BaseModel):
    # Elements of B.4.b
    aggregate_principal: float
    aggregate_value: float
    asset_type: str


class ClassReturn(BaseModel):
    # Elements of B.5.a
    return_month1: float
    return_month2: float
    return_month3: float
    class_identification: str


class Fund(BaseModel):
    # Foreign key to registrant
    registrant: Registrant

    # Elements of B.1
    total_assets: float
    total_liabilities: float
    net_assets: float

    # Elements of B.2
    misc_assets: float
    controlled_foreign_corporation_assets: float
    borrowings_short_bank: float
    borrowings_short_companies: float
    borrowings_short_affiliates: float
    borrowings_short_others: float
    borrowings_medium_bank: float
    borrowings_medium_companies: float
    borrowings_medium_affiliates: float
    borrowings_medium_others: float
    payables_delayed: float
    payables_standby: float
    liquidation_preference: float
    cash: float

    # Elements of B.3
    interest_risk: Optional[list[PortfolioInterestRisk]]
    credit_risk: Optional[PortfolioCreditRisk]

    # Elements of B.4
    borrowers: Optional[list[Borrower]]
    is_non_cash_collateral: bool
    non_cash_collateral: Optional[list[NonCashCollateral]]

    # Elements of B.5
    class_returns: list[ClassReturn]
