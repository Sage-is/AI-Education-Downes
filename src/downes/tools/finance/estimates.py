from langchain.tools import tool
from typing import Literal
from pydantic import BaseModel, Field
from downes.tools.finance.providers.config import ProviderFactory

# Initialize the default provider
_provider = ProviderFactory.get_composite_provider()


class AnalystEstimatesInput(BaseModel):
    """Input for get_analyst_estimates."""

    ticker: str = Field(
        ...,
        description="The stock ticker symbol to fetch analyst estimates for. For example, 'AAPL' for Apple.",
    )
    period: Literal["annual", "quarterly"] = Field(
        default="annual",
        description="The period for the estimates, either 'annual' or 'quarterly'.",
    )


@tool(args_schema=AnalystEstimatesInput)
def get_analyst_estimates(
    ticker: str,
    period: Literal["annual", "quarterly"] = "annual",
) -> dict:
    """
    Retrieves analyst estimates for a given company ticker, including metrics like estimated EPS.
    Useful for understanding consensus expectations, assessing future growth prospects, and performing valuation analysis.
    Note: Not all data providers support analyst estimates. Free providers may not include this data.
    """
    try:
        return _provider.get_analyst_estimates(ticker, period)
    except NotImplementedError:
        return {
            "error": "Analyst estimates not available with current data provider. Consider using a paid provider."
        }
