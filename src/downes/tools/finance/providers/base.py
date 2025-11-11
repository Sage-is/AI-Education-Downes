"""
Base abstract class for financial data providers.

This module defines the interface that all data providers must implement.
"""

from abc import ABC, abstractmethod
from typing import Literal, Optional, Any


class DataProvider(ABC):
    """
    Abstract base class for financial data providers.

    All data providers must implement these methods to provide a consistent interface
    for fetching financial data from various sources (Yahoo Finance, Alpha Vantage,
    trading APIs, etc.).
    """

    def __init__(this, api_key: Optional[str] = None, **kwargs):
        """
        Initialize the data provider.

        Args:
            api_key: Optional API key for the data source
            **kwargs: Additional provider-specific configuration
        """
        this.api_key = api_key
        this.config = kwargs

    @abstractmethod
    def get_income_statements(
        this,
        ticker: str,
        period: Literal["annual", "quarterly", "ttm"],
        limit: int = 10,
        **kwargs,
    ) -> dict:
        """Fetch income statements for a company."""
        pass

    @abstractmethod
    def get_balance_sheets(
        this,
        ticker: str,
        period: Literal["annual", "quarterly", "ttm"],
        limit: int = 10,
        **kwargs,
    ) -> dict:
        """Fetch balance sheets for a company."""
        pass

    @abstractmethod
    def get_cash_flow_statements(
        this,
        ticker: str,
        period: Literal["annual", "quarterly", "ttm"],
        limit: int = 10,
        **kwargs,
    ) -> dict:
        """Fetch cash flow statements for a company."""
        pass

    @abstractmethod
    def get_price_snapshot(this, ticker: str) -> dict:
        """Fetch the most recent price snapshot for a stock."""
        pass

    @abstractmethod
    def get_prices(
        this,
        ticker: str,
        interval: Literal["minute", "day", "week", "month", "year"],
        interval_multiplier: int,
        start_date: str,
        end_date: str,
    ) -> dict:
        """Fetch historical price data for a stock."""
        pass

    @abstractmethod
    def get_news(
        this,
        ticker: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 5,
    ) -> dict:
        """Fetch news articles for a company."""
        pass

    @abstractmethod
    def get_financial_metrics_snapshot(this, ticker: str) -> dict:
        """Fetch a snapshot of current financial metrics."""
        pass

    @abstractmethod
    def get_financial_metrics(
        this,
        ticker: str,
        period: Literal["annual", "quarterly", "ttm"] = "ttm",
        limit: int = 4,
        **kwargs,
    ) -> dict:
        """Fetch historical financial metrics."""
        pass

    def get_filings(
        this,
        ticker: str,
        filing_type: Optional[Literal["10-K", "10-Q", "8-K"]] = None,
        limit: int = 10,
    ) -> list[dict]:
        """Fetch SEC filings metadata. Optional - not all providers support this."""
        raise NotImplementedError(
            f"{this.__class__.__name__} does not support SEC filings"
        )

    def get_10K_filing_items(
        this, ticker: str, year: int, item: list[str] | None = None
    ) -> dict:
        """Fetch 10-K filing items. Optional - not all providers support this."""
        raise NotImplementedError(
            f"{this.__class__.__name__} does not support 10-K filings"
        )

    def get_10Q_filing_items(
        this, ticker: str, year: int, quarter: int, item: list[str] | None = None
    ) -> dict:
        """Fetch 10-Q filing items. Optional - not all providers support this."""
        raise NotImplementedError(
            f"{this.__class__.__name__} does not support 10-Q filings"
        )

    def get_8K_filing_items(
        this,
        ticker: str,
        accession_number: str,
    ) -> dict:
        """Fetch 8-K filing items. Optional - not all providers support this."""
        raise NotImplementedError(
            f"{this.__class__.__name__} does not support 8-K filings"
        )

    def get_analyst_estimates(
        this,
        ticker: str,
        period: Literal["annual", "quarterly"] = "annual",
    ) -> dict:
        """Fetch analyst estimates. Optional - not all providers support this."""
        raise NotImplementedError(
            f"{this.__class__.__name__} does not support analyst estimates"
        )

    def get_segmented_revenues(
        this,
        ticker: str,
        period: Literal["annual", "quarterly"],
        limit: int = 10,
    ) -> dict:
        """Fetch segmented revenue data. Optional - not all providers support this."""
        raise NotImplementedError(
            f"{this.__class__.__name__} does not support segmented revenues"
        )
