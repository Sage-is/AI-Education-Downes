from langchain.tools import tool
from typing import Literal
from pydantic import BaseModel, Field
from downes.tools.finance.providers.config import ProviderFactory

# Initialize the default provider
_provider = ProviderFactory.get_composite_provider()

####################################
# Tools
####################################


class SegmentedRevenuesInput(BaseModel):
    """Input for the get_segmented_revenues tool."""

    ticker: str = Field(
        description="The stock ticker symbol to fetch segmented revenues for. For example, 'AAPL' for Apple."
    )
    period: Literal["annual", "quarterly"] = Field(
        description="The reporting period for the segmented revenues. 'annual' for yearly, 'quarterly' for quarterly."
    )
    limit: int = Field(
        default=10, description="The number of past periods to retrieve."
    )


@tool(args_schema=SegmentedRevenuesInput)
def get_segmented_revenues(
    ticker: str,
    period: Literal["annual", "quarterly"],
    limit: int = 10,
) -> dict:
    """Provides a detailed breakdown of a company's revenue by operating segments, such as products, services, or geographic regions.
    Useful for analyzing the composition of a company's revenue.
    Note: Not all data providers support segmented revenues. Free providers may not include this data.
    """
    try:
        return _provider.get_segmented_revenues(ticker, period, limit)
    except NotImplementedError:
        return {
            "error": "Segmented revenues not available with current data provider. Consider using a paid provider."
        }
