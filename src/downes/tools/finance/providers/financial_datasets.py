"""
Financial Datasets API provider (legacy/paid option).

This is the original paid data source. It requires an API key from financialdatasets.ai
Users can optionally use this if they have an API key, but it's no longer required.
"""

import os
import requests
from typing import Literal, Optional
from .base import DataProvider


class FinancialDatasetsProvider(DataProvider):
    """
    Provider for Financial Datasets API (paid service).

    Requires API key from https://financialdatasets.ai

    This is a legacy/optional provider. The project now defaults to free sources
    like Yahoo Finance, but users can still use this if they have an API key.
    """

    BASE_URL = "https://api.financialdatasets.ai"

    def __init__(this, api_key: Optional[str] = None, **kwargs):
        """Initialize with API key."""
        api_key = api_key or os.getenv("FINANCIAL_DATASETS_API_KEY")
        if not api_key:
            raise ValueError(
                "FINANCIAL_DATASETS_API_KEY required for FinancialDatasetsProvider. "
                "Set environment variable or use free providers like YahooFinanceProvider."
            )
        super().__init__(api_key=api_key, **kwargs)

    def _call_api(this, endpoint: str, params: dict) -> dict:
        """Helper function to call the Financial Datasets API."""
        url = f"{this.BASE_URL}{endpoint}"
        headers = {"x-api-key": this.api_key}
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_income_statements(
        this,
        ticker: str,
        period: Literal["annual", "quarterly", "ttm"],
        limit: int = 10,
        **kwargs,
    ) -> dict:
        params = {"ticker": ticker, "period": period, "limit": limit}
        for key in [
            "report_period_gt",
            "report_period_gte",
            "report_period_lt",
            "report_period_lte",
        ]:
            if key in kwargs and kwargs[key] is not None:
                params[key] = kwargs[key]
        data = this._call_api("/financials/income-statements/", params)
        return data.get("income_statements", {})

    def get_balance_sheets(
        this,
        ticker: str,
        period: Literal["annual", "quarterly", "ttm"],
        limit: int = 10,
        **kwargs,
    ) -> dict:
        params = {"ticker": ticker, "period": period, "limit": limit}
        for key in [
            "report_period_gt",
            "report_period_gte",
            "report_period_lt",
            "report_period_lte",
        ]:
            if key in kwargs and kwargs[key] is not None:
                params[key] = kwargs[key]
        data = this._call_api("/financials/balance-sheets/", params)
        return data.get("balance_sheets", {})

    def get_cash_flow_statements(
        this,
        ticker: str,
        period: Literal["annual", "quarterly", "ttm"],
        limit: int = 10,
        **kwargs,
    ) -> dict:
        params = {"ticker": ticker, "period": period, "limit": limit}
        for key in [
            "report_period_gt",
            "report_period_gte",
            "report_period_lt",
            "report_period_lte",
        ]:
            if key in kwargs and kwargs[key] is not None:
                params[key] = kwargs[key]
        data = this._call_api("/financials/cash-flow-statements/", params)
        return data.get("cash_flow_statements", {})

    def get_price_snapshot(this, ticker: str) -> dict:
        params = {"ticker": ticker}
        data = this._call_api("/prices/snapshot/", params)
        return data.get("snapshot", {})

    def get_prices(
        this,
        ticker: str,
        interval: Literal["minute", "day", "week", "month", "year"],
        interval_multiplier: int,
        start_date: str,
        end_date: str,
    ) -> dict:
        params = {
            "ticker": ticker,
            "interval": interval,
            "interval_multiplier": interval_multiplier,
            "start_date": start_date,
            "end_date": end_date,
        }
        data = this._call_api("/prices/", params)
        return data.get("prices", [])

    def get_news(
        this,
        ticker: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 5,
    ) -> dict:
        params = {"ticker": ticker, "limit": limit}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        data = this._call_api("/news/", params)
        return data.get("news", [])

    def get_financial_metrics_snapshot(this, ticker: str) -> dict:
        params = {"ticker": ticker}
        data = this._call_api("/financial-metrics/snapshot/", params)
        return data.get("snapshot", {})

    def get_financial_metrics(
        this,
        ticker: str,
        period: Literal["annual", "quarterly", "ttm"] = "ttm",
        limit: int = 4,
        **kwargs,
    ) -> dict:
        params = {"ticker": ticker, "period": period, "limit": limit}
        for key in [
            "report_period",
            "report_period_gt",
            "report_period_gte",
            "report_period_lt",
            "report_period_lte",
        ]:
            if key in kwargs and kwargs[key] is not None:
                params[key] = kwargs[key]
        data = this._call_api("/financial-metrics/", params)
        return data.get("financial_metrics", [])

    def get_filings(
        this,
        ticker: str,
        filing_type: Optional[Literal["10-K", "10-Q", "8-K"]] = None,
        limit: int = 10,
    ) -> list[dict]:
        params = {"ticker": ticker, "limit": limit}
        if filing_type is not None:
            params["filing_type"] = filing_type
        data = this._call_api("/filings/", params)
        return data.get("filings", [])

    def get_analyst_estimates(
        this, ticker: str, period: Literal["annual", "quarterly"] = "annual"
    ) -> dict:
        params = {"ticker": ticker, "period": period}
        data = this._call_api("/analyst-estimates/", params)
        return data.get("analyst_estimates", [])

    def get_segmented_revenues(
        this, ticker: str, period: Literal["annual", "quarterly"], limit: int = 10
    ) -> dict:
        params = {"ticker": ticker, "period": period, "limit": limit}
        data = this._call_api("/financials/segmented-revenues/", params)
        return data.get("segmented_revenues", {})
