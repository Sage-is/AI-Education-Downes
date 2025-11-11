from langchain.tools import tool
from typing import Literal, Optional
from pydantic import BaseModel, Field
from downes.tools.finance.providers.config import ProviderFactory

# Initialize the default provider (auto-selects based on available API keys)
_provider = ProviderFactory.get_composite_provider()

####################################
# Tools
####################################


class FinancialStatementsInput(BaseModel):
    ticker: str = Field(
        description="The stock ticker symbol to fetch financial statements for. For example, 'AAPL' for Apple."
    )
    period: Literal["annual", "quarterly", "ttm"] = Field(
        description="The reporting period for the financial statements. 'annual' for yearly, 'quarterly' for quarterly, and 'ttm' for trailing twelve months."
    )
    limit: int = Field(
        default=10, description="The number of past financial statements to retrieve."
    )
    report_period_gt: Optional[str] = Field(
        default=None,
        description="Filter for financial statements with report periods after this date (YYYY-MM-DD).",
    )
    report_period_gte: Optional[str] = Field(
        default=None,
        description="Filter for financial statements with report periods on or after this date (YYYY-MM-DD).",
    )
    report_period_lt: Optional[str] = Field(
        default=None,
        description="Filter for financial statements with report periods before this date (YYYY-MM-DD).",
    )
    report_period_lte: Optional[str] = Field(
        default=None,
        description="Filter for financial statements with report periods on or before this date (YYYY-MM-DD).",
    )


@tool(args_schema=FinancialStatementsInput)
def get_income_statements(
    ticker: str,
    period: Literal["annual", "quarterly", "ttm"],
    limit: int = 10,
    report_period_gt: Optional[str] = None,
    report_period_gte: Optional[str] = None,
    report_period_lt: Optional[str] = None,
    report_period_lte: Optional[str] = None,
) -> dict:
    """
    Fetches a company's income statements,
    detailing its revenues, expenses, net income, etc. over a reporting period.
    Useful for evaluating a company's profitability and operational efficiency.
    """
    return _provider.get_income_statements(
        ticker,
        period,
        limit,
        report_period_gt=report_period_gt,
        report_period_gte=report_period_gte,
        report_period_lt=report_period_lt,
        report_period_lte=report_period_lte,
    )


@tool(args_schema=FinancialStatementsInput)
def get_balance_sheets(
    ticker: str,
    period: Literal["annual", "quarterly", "ttm"],
    limit: int = 10,
    report_period_gt: Optional[str] = None,
    report_period_gte: Optional[str] = None,
    report_period_lt: Optional[str] = None,
    report_period_lte: Optional[str] = None,
) -> dict:
    """
    Retrieves a company's balance sheets, providing a snapshot of
    its assets, liabilities, shareholders' equity, etc. at a specific point in time.
    Useful for assessing a company's financial position.
    """
    return _provider.get_balance_sheets(
        ticker,
        period,
        limit,
        report_period_gt=report_period_gt,
        report_period_gte=report_period_gte,
        report_period_lt=report_period_lt,
        report_period_lte=report_period_lte,
    )


@tool(args_schema=FinancialStatementsInput)
def get_cash_flow_statements(
    ticker: str,
    period: Literal["annual", "quarterly", "ttm"],
    limit: int = 10,
    report_period_gt: Optional[str] = None,
    report_period_gte: Optional[str] = None,
    report_period_lt: Optional[str] = None,
    report_period_lte: Optional[str] = None,
) -> dict:
    """
    Retrieves a company's cash flow statements,
    showing how cash is generated and used across
    operating, investing, and financing activities.
    Useful for understanding a company's liquidity and solvency.
    """
    return _provider.get_cash_flow_statements(
        ticker,
        period,
        limit,
        report_period_gt=report_period_gt,
        report_period_gte=report_period_gte,
        report_period_lt=report_period_lt,
        report_period_lte=report_period_lte,
    )
