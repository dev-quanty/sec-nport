from typing import Optional
from datetime import date
from decimal import Decimal
from pydantic import BaseModel
from nport.xmltools import find_element, child_text, child_value, optional_decimal_text, optional_decimal_value


class BaseInstrument(BaseModel):
    # Elements of C.1
    issuer: str
    lei: Optional[str]
    name: str
    cusip: Optional[str]
    isin: Optional[str]
    ticker: Optional[str]
    other_identifier_name: Optional[str]
    other_identifier: Optional[str]

    # Elements of C.2 and C.3
    balance: float
    value_usd: float
    value_local: float
    price_usd: float
    price_local: float
    units: str
    units_description: Optional[str]
    currency: str
    exchange_rate: Optional[float]
    fund_percentage: float
    payoff_profile: Optional[str]

    # Elements of C.4, C.5 and C.6
    asset_type: str
    asset_description: Optional[str]
    issuer_type: str
    issuer_description: Optional[str]
    issuer_country: str
    issuer_country_exposure: Optional[str]
    is_restricted_security: bool

    # Elements of C.7 and C.8
    liquidity: Optional[int]
    fair_value_level: Optional[int]

    # Elements of C.12
    is_cash_collateral_value: bool
    cash_collateral_value: Optional[float]
    is_non_cash_collateral: bool
    non_cash_collateral_value: Optional[float]
    is_on_loan: bool
    on_loan_value: Optional[float]

    # Additional from A.3
    report_date: date

    @classmethod
    def from_xml(cls, tag, report_date):
        issuer = child_text(tag, "name")
        lei = child_text(tag, "lei")
        name = child_text(tag, "title")
        cusip = child_text(tag, "cusip")

        identifiers_tag = tag.find("identifiers")
        ticker = child_value(identifiers_tag, "ticker")
        isin = child_value(identifiers_tag, "isin")
        other_identifier_name = child_value(identifiers_tag, "other", "otherDesc")
        other_identifier = child_value(identifiers_tag, "other")

        balance = optional_decimal_text(tag, "balance")
        value_usd = optional_decimal_text(tag, "valUSD")
        units = child_text(tag, "units")
        units_description = child_text(tag, "descOthUnits")
        currency = child_text(tag, "curCd")
        exchange_rate = None
        if currency is None:
            currency = child_value(tag, "currencyConditional", "curCd")
            exchange_rate = optional_decimal_value(tag, "currencyConditional", "exchangeRt")
        fund_percentage = optional_decimal_text(tag, "pctVal")
        payoff_profile = child_text(tag, "payoffProfile")

        value_local = None
        price_usd = None
        price_local = None
        if currency and currency != "USD" and exchange_rate:
            value_local = exchange_rate * value_usd
        elif currency and currency == "USD":
            value_local = value_usd
        price_local = value_local / balance
        price_usd = value_usd / balance
        if units == "PA":
            price_usd = 100 * price_usd
            price_local = 100 * price_local
        if payoff_profile == "Short":
            price_usd = -1 * price_usd
            price_local = -1 * price_local

        asset_type = child_text(tag, "assetCat")
        asset_description = None
        if asset_type is None:
            asset_type = child_value(tag, "assetConditional", "assetCat")
            asset_description = child_value(tag, "assetConditional", "desc")
        issuer_type = child_text(tag, "issuerCat")
        issuer_description = None
        if issuer_type is None:
            issuer_type = child_value(tag, "issuerConditional", "issuerCat")
            issuer_description = child_value(tag, "issuerConditional", "desc")
        issuer_country = child_text(tag, "invCountry")
        issuer_country_exposure = child_text(tag, "invOthCountry")
        is_restricted_security = child_text(tag, "isRestrictedSec") == "Y"

        liquidity = child_text(tag, "fundCat")
        fair_value_level = child_text(tag, "fairValLevel")

        security_lending_tag = tag.find("securityLending")
        is_cash_collateral_value = child_text(security_lending_tag, "isCashCollateral")
        cash_collateral_value = None
        if is_cash_collateral_value is None:
            is_cash_collateral_value = child_value(security_lending_tag, "cashCollateralCondition", "isCashCollateral")
            cash_collateral_value = child_value(security_lending_tag, "cashCollateralCondition", "cashCollateralVal")
        is_cash_collateral_value = is_cash_collateral_value == "Y"

        is_non_cash_collateral = child_text(security_lending_tag, "isNonCashCollateral")
        non_cash_collateral_value = None
        if is_non_cash_collateral is None:
            is_non_cash_collateral = child_value(security_lending_tag, "nonCashCollateralCondition", "isNonCashCollateral")
            non_cash_collateral_value = child_value(security_lending_tag, "nonCashCollateralCondition", "nonCashCollateralVal")
        is_non_cash_collateral = is_non_cash_collateral == "Y"

        is_on_loan = child_text(security_lending_tag, "isLoanByFund")
        on_loan_value = None
        if is_on_loan is None:
            is_on_loan = child_value(security_lending_tag, "loanByFundCondition", "isLoanByFund")
            on_loan_value = child_value(security_lending_tag, "loanByFundCondition", "loanVal")
        is_on_loan = is_on_loan == "Y"

        return cls(
            issuer=issuer,
            lei=lei,
            name=name,
            cusip=cusip,
            isin=isin,
            ticker=ticker,
            other_identifier_name=other_identifier_name,
            other_identifier=other_identifier,
            balance=balance,
            value_usd=value_usd,
            value_local=value_local,
            price_usd=price_usd,
            price_local=price_local,
            units=units,
            units_description=units_description,
            currency=currency,
            exchange_rate=exchange_rate,
            fund_percentage=fund_percentage,
            payoff_profile=payoff_profile,
            asset_type=asset_type,
            asset_description=asset_description,
            issuer_type=issuer_type,
            issuer_description=issuer_description,
            issuer_country=issuer_country,
            issuer_country_exposure=issuer_country_exposure,
            is_restricted_security=is_restricted_security,
            liquidity=liquidity,
            fair_value_level=fair_value_level,
            is_cash_collateral_value=is_cash_collateral_value,
            cash_collateral_value=cash_collateral_value,
            is_non_cash_collateral=is_non_cash_collateral,
            non_cash_collateral_value=non_cash_collateral_value,
            is_on_loan=is_on_loan,
            on_loan_value=on_loan_value,
            report_date=report_date
        )

    def __repr__(self):
        return f"{self.name} [{self.issuer}]"

    def __str__(self):
        return self.__repr__()


class DebtSecurity(BaseInstrument):
    # Elements of C.9
    maturity_date: date
    coupon_type: Optional[str]
    coupon_rate: Optional[float]
    is_default: bool
    is_deferred_interest: bool
    is_paid_in_kind: bool
    is_mandatory_convertible: Optional[bool]
    is_contingent_convertible: Optional[bool]
    reference_issuer: Optional[str]
    reference_name: Optional[str]
    reference_currency: Optional[str]
    reference_cusip: Optional[str]
    reference_isin: Optional[str]
    reference_ticker: Optional[str]
    reference_other_identifier_name: Optional[str]
    reference_other_identifier: Optional[str]
    conversion_ratio: Optional[float]
    conversion_currency: Optional[str]
    delta: Optional[float]

    @classmethod
    def from_xml(cls, tag, report_date):
        debt_security_tag = tag.find("debtSec")
        maturity_date = child_text(debt_security_tag, "maturityDt")
        coupon_type = child_text(debt_security_tag, "couponKind")
        coupon_rate = optional_decimal_text(debt_security_tag, "annualizedRt")
        is_default = child_text(debt_security_tag, "isDefault") == "Y"
        is_deferred_interest = child_text(debt_security_tag, "areIntrstPmntsInArrs") == "Y"
        is_paid_in_kind = child_text(debt_security_tag, "isPaidKind")

        is_mandatory_convertible = child_text(debt_security_tag, "isMandatoryConvrtbl")
        if is_mandatory_convertible:
            is_mandatory_convertible = is_mandatory_convertible == "Y"
        is_contingent_convertible = child_text(debt_security_tag, "isContngtConvrtbl")
        if is_contingent_convertible:
            is_contingent_convertible = is_contingent_convertible == "Y"

        reference_issuer = None
        reference_name = None
        reference_currency = None
        reference_cusip = None
        reference_isin = None
        reference_ticker = None
        reference_other_identifier_name = None
        reference_other_identifier = None
        reference_tag = debt_security_tag.find("dbtSecRefInstruments")
        if reference_tag:
            reference_issuer = child_text(reference_tag, "name")
            reference_name = child_text(reference_tag, "title")
            reference_currency = child_text(reference_tag, "curCd")
            reference_identifier_tag = reference_tag.find("identifiers")
            reference_cusip = child_value(reference_identifier_tag, "cusip")
            reference_isin = child_value(reference_identifier_tag, "isin")
            reference_ticker = child_value(reference_identifier_tag, "ticker")
            reference_other_identifier_name = child_value(reference_identifier_tag, "other", "otherDesc")
            reference_other_identifier = child_value(reference_identifier_tag, "other")

        conversion_ratio = None
        conversion_currency = None
        currency_info_tag = debt_security_tag.find("currencyInfos")
        if currency_info_tag:
            conversion_ratio = child_value(currency_info_tag, "currencyInfo", "convRatio")
            conversion_currency = child_value(currency_info_tag, "currencyInfo", "curCd")
        delta = optional_decimal_text(debt_security_tag, "delta")

        base = BaseInstrument.from_xml(tag, report_date)
        return cls(
            **base.__dict__,
            maturity_date=maturity_date,
            coupon_type=coupon_type,
            coupon_rate=coupon_rate,
            is_default=is_default,
            is_deferred_interest=is_deferred_interest,
            is_paid_in_kind=is_paid_in_kind,
            is_mandatory_convertible=is_mandatory_convertible,
            is_contingent_convertible=is_contingent_convertible,
            reference_issuer=reference_issuer,
            reference_name=reference_name,
            reference_currency=reference_currency,
            reference_cusip=reference_cusip,
            reference_isin=reference_isin,
            reference_ticker=reference_ticker,
            reference_other_identifier_name=reference_other_identifier_name,
            reference_other_identifier=reference_other_identifier,
            conversion_ratio=conversion_ratio,
            conversion_currency=conversion_currency,
            delta=delta
        )


class RepurchasementAgreement(BaseInstrument):
    # Elements of C.10
    agreement_category: str
    is_cleared_by_central_counterparty: bool
    counterparty_name: Optional[str]
    counterparty_lei: Optional[str]
    is_triparty: bool
    repurchase_rate: float
    maturity_date: date
    principal: float
    collateral: float
    collateral_type: str


class Derivative(BaseInstrument):
    # Elements of C.11
    derivative_type: str
    counterparty_name: Optional[str]
    counterparty_lei: Optional[str]
    option_type: str
    option_payoff: str
    reference_issuer: Optional[str]
    reference_name: Optional[str]
    reference_currency: Optional[str]
    reference_cusip: Optional[str]
    reference_isin: Optional[str]
    reference_ticker: Optional[str]
    reference_other_identifier_name: Optional[str]
    reference_other_identifier: Optional[str]
    principal_or_shares: float
    exercise_price: float
    exercise_currency: str
    exercise_date: date
    delta: Optional[float]
    unrealized_appreciation: float
