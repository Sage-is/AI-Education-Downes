"""
Provider configuration and factory for creating data provider instances.

This module handles selecting and initializing the appropriate data provider
based on configuration and available API keys.
"""

import os
from typing import Optional, Literal
from .base import DataProvider
from .yahoo_finance import YahooFinanceProvider
from .sec_edgar import SECEdgarProvider


class ProviderFactory:
    """Factory for creating and managing data provider instances."""

    # Default provider priority (if no preference specified)
    DEFAULT_PRIORITY = ["yahoo", "sec"]

    @staticmethod
    def create_provider(provider_name: Optional[str] = None, **kwargs) -> DataProvider:
        """
        Create a data provider instance.

        Args:
            provider_name: Name of provider to use ('yahoo', 'sec', 'financial_datasets').
                          If None, will auto-select based on available API keys.
            **kwargs: Provider-specific configuration

        Returns:
            Initialized DataProvider instance

        Raises:
            ValueError: If provider_name is invalid or no suitable provider found
        """

        # Auto-select provider if not specified
        if provider_name is None:
            provider_name = ProviderFactory._auto_select_provider()

        provider_name = provider_name.lower()

        if provider_name == "yahoo":
            return YahooFinanceProvider(**kwargs)
        elif provider_name == "sec":
            user_agent = kwargs.get(
                "user_agent",
                os.getenv(
                    "SEC_USER_AGENT", "Financial Research Agent contact@example.com"
                ),
            )
            return SECEdgarProvider(user_agent=user_agent, **kwargs)
        elif provider_name == "financial_datasets":
            # Legacy support for Financial Datasets API (if user still has API key)
            from .financial_datasets import FinancialDatasetsProvider

            api_key = kwargs.get("api_key", os.getenv("FINANCIAL_DATASETS_API_KEY"))
            if not api_key:
                raise ValueError(
                    "FINANCIAL_DATASETS_API_KEY not found. "
                    "Either set the environment variable or use a free provider like 'yahoo'."
                )
            return FinancialDatasetsProvider(api_key=api_key, **kwargs)
        else:
            raise ValueError(
                f"Unknown provider: {provider_name}. "
                f"Supported providers: yahoo, sec, financial_datasets"
            )

    @staticmethod
    def _auto_select_provider() -> str:
        """
        Auto-select the best available provider based on environment.

        Returns:
            Provider name to use
        """
        # Check if user has Financial Datasets API key (legacy)
        if os.getenv("FINANCIAL_DATASETS_API_KEY"):
            return "financial_datasets"

        # Default to free Yahoo Finance
        return "yahoo"

    @staticmethod
    def get_composite_provider(**kwargs) -> "CompositeProvider":
        """
        Create a composite provider that combines multiple providers.
        Uses Yahoo Finance for prices/fundamentals and SEC for filings.

        Returns:
            CompositeProvider instance
        """
        return CompositeProvider(**kwargs)


class CompositeProvider(DataProvider):
    """
    Composite provider that combines multiple providers for best coverage.

    Uses:
    - Yahoo Finance for: prices, fundamentals, news, metrics
    - SEC EDGAR for: filings
    """

    def __init__(this, **kwargs):
        """Initialize composite provider with multiple backends."""
        super().__init__(**kwargs)
        this.yahoo = YahooFinanceProvider(**kwargs)
        this.sec = SECEdgarProvider(**kwargs)

    # Delegate to Yahoo Finance for these
    def get_income_statements(
        this,
        ticker: str,
        period: Literal["annual", "quarterly", "ttm"],
        limit: int = 10,
        **kwargs,
    ) -> dict:
        return this.yahoo.get_income_statements(ticker, period, limit, **kwargs)

    def get_balance_sheets(
        this,
        ticker: str,
        period: Literal["annual", "quarterly", "ttm"],
        limit: int = 10,
        **kwargs,
    ) -> dict:
        return this.yahoo.get_balance_sheets(ticker, period, limit, **kwargs)

    def get_cash_flow_statements(
        this,
        ticker: str,
        period: Literal["annual", "quarterly", "ttm"],
        limit: int = 10,
        **kwargs,
    ) -> dict:
        return this.yahoo.get_cash_flow_statements(ticker, period, limit, **kwargs)

    def get_price_snapshot(this, ticker: str) -> dict:
        return this.yahoo.get_price_snapshot(ticker)

    def get_prices(
        this,
        ticker: str,
        interval: Literal["minute", "day", "week", "month", "year"],
        interval_multiplier: int,
        start_date: str,
        end_date: str,
    ) -> dict:
        return this.yahoo.get_prices(
            ticker, interval, interval_multiplier, start_date, end_date
        )

    def get_news(
        this,
        ticker: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 5,
    ) -> dict:
        return this.yahoo.get_news(ticker, start_date, end_date, limit)

    def get_financial_metrics_snapshot(this, ticker: str) -> dict:
        return this.yahoo.get_financial_metrics_snapshot(ticker)

    def get_financial_metrics(
        this,
        ticker: str,
        period: Literal["annual", "quarterly", "ttm"] = "ttm",
        limit: int = 4,
        **kwargs,
    ) -> dict:
        return this.yahoo.get_financial_metrics(ticker, period, limit, **kwargs)

    # Delegate to SEC EDGAR for filings
    def get_filings(
        this,
        ticker: str,
        filing_type: Optional[Literal["10-K", "10-Q", "8-K"]] = None,
        limit: int = 10,
    ) -> list[dict]:
        return this.sec.get_filings(ticker, filing_type, limit)
