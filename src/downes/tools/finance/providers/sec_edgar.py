"""
SEC EDGAR data provider for fetching SEC filings.

This provider is completely free and doesn't require any API keys.
Uses the SEC's public EDGAR database.
"""

from typing import Literal, Optional
import requests
from datetime import datetime
from .base import DataProvider


class SECEdgarProvider(DataProvider):
    """
    Free SEC EDGAR data provider for SEC filings.

    No API key required. Provides:
    - SEC filings metadata (10-K, 10-Q, 8-K)
    - Filing content and items

    Does NOT provide:
    - Stock prices (use YahooFinanceProvider)
    - Financial statements in structured format (use YahooFinanceProvider)
    - News (use YahooFinanceProvider)
    """

    BASE_URL = "https://data.sec.gov"

    def __init__(
        this, user_agent: str = "Financial Research Agent contact@example.com", **kwargs
    ):
        """
        Initialize SEC EDGAR provider.

        Args:
            user_agent: Required by SEC. Should include contact information.
        """
        super().__init__(api_key=None, **kwargs)
        this.headers = {"User-Agent": user_agent, "Accept-Encoding": "gzip, deflate"}

    def _get_cik(this, ticker: str) -> str:
        """
        Get CIK number for a ticker symbol.
        Uses SEC's company tickers JSON.
        """
        url = "https://www.sec.gov/files/company_tickers.json"
        response = requests.get(url, headers=this.headers)
        response.raise_for_status()

        tickers = response.json()
        ticker_upper = ticker.upper()

        for entry in tickers.values():
            if entry.get("ticker") == ticker_upper:
                # CIK needs to be 10 digits with leading zeros
                return str(entry["cik_str"]).zfill(10)

        raise ValueError(f"Could not find CIK for ticker {ticker}")

    def get_filings(
        this,
        ticker: str,
        filing_type: Optional[Literal["10-K", "10-Q", "8-K"]] = None,
        limit: int = 10,
    ) -> list[dict]:
        """Fetch SEC filings metadata from EDGAR."""
        cik = this._get_cik(ticker)

        # Get submissions data
        url = f"{this.BASE_URL}/submissions/CIK{cik}.json"
        response = requests.get(url, headers=this.headers)
        response.raise_for_status()

        data = response.json()
        filings_data = data.get("filings", {}).get("recent", {})

        if not filings_data:
            return []

        # Parse filings
        filings = []
        num_filings = len(filings_data.get("accessionNumber", []))

        for i in range(num_filings):
            form = filings_data["form"][i]

            # Filter by filing type if specified
            if filing_type and form != filing_type:
                continue

            filing = {
                "accession_number": filings_data["accessionNumber"][i],
                "filing_type": form,
                "filing_date": filings_data["filingDate"][i],
                "report_date": filings_data.get("reportDate", [None] * num_filings)[i],
                "primary_document": filings_data.get(
                    "primaryDocument", [None] * num_filings
                )[i],
            }
            filings.append(filing)

            if len(filings) >= limit:
                break

        return filings

    # Methods that SEC doesn't provide - raise NotImplementedError
    def get_income_statements(
        this,
        ticker: str,
        period: Literal["annual", "quarterly", "ttm"],
        limit: int = 10,
        **kwargs,
    ) -> dict:
        """SEC EDGAR doesn't provide structured financial statements. Use YahooFinanceProvider."""
        raise NotImplementedError(
            "SEC EDGAR doesn't provide structured financial statements. Use YahooFinanceProvider instead."
        )

    def get_balance_sheets(
        this,
        ticker: str,
        period: Literal["annual", "quarterly", "ttm"],
        limit: int = 10,
        **kwargs,
    ) -> dict:
        """SEC EDGAR doesn't provide structured financial statements. Use YahooFinanceProvider."""
        raise NotImplementedError(
            "SEC EDGAR doesn't provide structured financial statements. Use YahooFinanceProvider instead."
        )

    def get_cash_flow_statements(
        this,
        ticker: str,
        period: Literal["annual", "quarterly", "ttm"],
        limit: int = 10,
        **kwargs,
    ) -> dict:
        """SEC EDGAR doesn't provide structured financial statements. Use YahooFinanceProvider."""
        raise NotImplementedError(
            "SEC EDGAR doesn't provide structured financial statements. Use YahooFinanceProvider instead."
        )

    def get_price_snapshot(this, ticker: str) -> dict:
        """SEC doesn't provide price data. Use YahooFinanceProvider."""
        raise NotImplementedError(
            "SEC doesn't provide price data. Use YahooFinanceProvider instead."
        )

    def get_prices(
        this,
        ticker: str,
        interval: Literal["minute", "day", "week", "month", "year"],
        interval_multiplier: int,
        start_date: str,
        end_date: str,
    ) -> dict:
        """SEC doesn't provide price data. Use YahooFinanceProvider."""
        raise NotImplementedError(
            "SEC doesn't provide price data. Use YahooFinanceProvider instead."
        )

    def get_news(
        this,
        ticker: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 5,
    ) -> dict:
        """SEC doesn't provide news. Use YahooFinanceProvider."""
        raise NotImplementedError(
            "SEC doesn't provide news. Use YahooFinanceProvider instead."
        )

    def get_financial_metrics_snapshot(this, ticker: str) -> dict:
        """SEC doesn't provide financial metrics. Use YahooFinanceProvider."""
        raise NotImplementedError(
            "SEC doesn't provide financial metrics. Use YahooFinanceProvider instead."
        )

    def get_financial_metrics(
        this,
        ticker: str,
        period: Literal["annual", "quarterly", "ttm"] = "ttm",
        limit: int = 4,
        **kwargs,
    ) -> dict:
        """SEC doesn't provide financial metrics. Use YahooFinanceProvider."""
        raise NotImplementedError(
            "SEC doesn't provide financial metrics. Use YahooFinanceProvider instead."
        )
