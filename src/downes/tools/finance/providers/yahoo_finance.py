"""
Yahoo Finance data provider implementation using yfinance library.

This provider is completely free and doesn't require any API keys.
"""

from typing import Literal, Optional
from datetime import datetime, timedelta
from .base import DataProvider

try:
    import yfinance as yf
except ImportError:
    raise ImportError(
        "yfinance is required for YahooFinanceProvider. "
        "Install it with: pip install yfinance"
    )


class YahooFinanceProvider(DataProvider):
    """
    Free data provider using Yahoo Finance API via yfinance library.

    No API key required. Provides:
    - Stock prices (historical and snapshot)
    - Financial statements (income, balance sheet, cash flow)
    - Basic financial metrics
    - Company news

    Does NOT provide:
    - SEC filings (use SECEdgarProvider)
    - Analyst estimates
    - Segmented revenues
    """

    def __init__(this, **kwargs):
        """Initialize Yahoo Finance provider (no API key needed)."""
        super().__init__(api_key=None, **kwargs)

    def _get_ticker(this, ticker: str):
        """Get yfinance Ticker object."""
        return yf.Ticker(ticker)

    def get_income_statements(
        this,
        ticker: str,
        period: Literal["annual", "quarterly", "ttm"],
        limit: int = 10,
        **kwargs,
    ) -> dict:
        """Fetch income statements from Yahoo Finance."""
        stock = this._get_ticker(ticker)

        if period == "annual":
            df = stock.financials
        elif period in ["quarterly", "ttm"]:
            df = stock.quarterly_financials
        else:
            return {}

        if df.empty:
            return {}

        # Convert to list of dicts format (most recent first)
        df = df.T.head(limit)
        statements = []

        for date, row in df.iterrows():
            statement = {
                "report_period": (
                    date.strftime("%Y-%m-%d")
                    if hasattr(date, "strftime")
                    else str(date)
                ),
                "period": period,
                "revenue": row.get("Total Revenue"),
                "cost_of_revenue": row.get("Cost Of Revenue"),
                "gross_profit": row.get("Gross Profit"),
                "operating_income": row.get("Operating Income"),
                "net_income": row.get("Net Income"),
                "ebitda": row.get("EBITDA"),
                "operating_expense": row.get("Operating Expense"),
            }
            # Remove None values and convert to float
            cleaned_statement = {}
            for k, v in statement.items():
                if k == "report_period" or k == "period":
                    cleaned_statement[k] = v
                elif v is not None and str(v) != "nan":
                    try:
                        cleaned_statement[k] = float(v)
                    except (ValueError, TypeError):
                        cleaned_statement[k] = None
                else:
                    cleaned_statement[k] = None
            statements.append(cleaned_statement)

        return statements

    def get_balance_sheets(
        this,
        ticker: str,
        period: Literal["annual", "quarterly", "ttm"],
        limit: int = 10,
        **kwargs,
    ) -> dict:
        """Fetch balance sheets from Yahoo Finance."""
        stock = this._get_ticker(ticker)

        if period == "annual":
            df = stock.balance_sheet
        elif period in ["quarterly", "ttm"]:
            df = stock.quarterly_balance_sheet
        else:
            return {}

        if df.empty:
            return {}

        # Convert to list of dicts format
        df = df.T.head(limit)
        statements = []

        for date, row in df.iterrows():
            statement = {
                "report_period": (
                    date.strftime("%Y-%m-%d")
                    if hasattr(date, "strftime")
                    else str(date)
                ),
                "period": period,
                "total_assets": row.get("Total Assets"),
                "total_liabilities": row.get("Total Liabilities Net Minority Interest"),
                "stockholders_equity": row.get("Stockholders Equity"),
                "cash_and_equivalents": row.get("Cash And Cash Equivalents"),
                "current_assets": row.get("Current Assets"),
                "current_liabilities": row.get("Current Liabilities"),
                "total_debt": row.get("Total Debt"),
            }
            cleaned_statement = {}
            for k, v in statement.items():
                if k in ["report_period", "period"]:
                    cleaned_statement[k] = v
                elif v is not None and str(v) != "nan":
                    try:
                        cleaned_statement[k] = float(v)
                    except (ValueError, TypeError):
                        cleaned_statement[k] = None
                else:
                    cleaned_statement[k] = None
            statements.append(cleaned_statement)

        return statements

    def get_cash_flow_statements(
        this,
        ticker: str,
        period: Literal["annual", "quarterly", "ttm"],
        limit: int = 10,
        **kwargs,
    ) -> dict:
        """Fetch cash flow statements from Yahoo Finance."""
        stock = this._get_ticker(ticker)

        if period == "annual":
            df = stock.cashflow
        elif period in ["quarterly", "ttm"]:
            df = stock.quarterly_cashflow
        else:
            return {}

        if df.empty:
            return {}

        # Convert to list of dicts format
        df = df.T.head(limit)
        statements = []

        for date, row in df.iterrows():
            statement = {
                "report_period": (
                    date.strftime("%Y-%m-%d")
                    if hasattr(date, "strftime")
                    else str(date)
                ),
                "period": period,
                "operating_cash_flow": row.get("Operating Cash Flow"),
                "investing_cash_flow": row.get("Investing Cash Flow"),
                "financing_cash_flow": row.get("Financing Cash Flow"),
                "free_cash_flow": row.get("Free Cash Flow"),
                "capital_expenditure": row.get("Capital Expenditure"),
            }
            cleaned_statement = {}
            for k, v in statement.items():
                if k in ["report_period", "period"]:
                    cleaned_statement[k] = v
                elif v is not None and str(v) != "nan":
                    try:
                        cleaned_statement[k] = float(v)
                    except (ValueError, TypeError):
                        cleaned_statement[k] = None
                else:
                    cleaned_statement[k] = None
            statements.append(cleaned_statement)

        return statements

    def get_price_snapshot(this, ticker: str) -> dict:
        """Fetch current price snapshot from Yahoo Finance."""
        stock = this._get_ticker(ticker)
        info = stock.info

        # Get most recent price data
        hist = stock.history(period="1d")

        if hist.empty:
            return {}

        latest = hist.iloc[-1]

        return {
            "ticker": ticker,
            "price": float(latest["Close"]) if "Close" in latest else None,
            "open": float(latest["Open"]) if "Open" in latest else None,
            "high": float(latest["High"]) if "High" in latest else None,
            "low": float(latest["Low"]) if "Low" in latest else None,
            "volume": int(latest["Volume"]) if "Volume" in latest else None,
            "previous_close": info.get("previousClose"),
            "change": info.get("regularMarketChange"),
            "change_percent": info.get("regularMarketChangePercent"),
        }

    def get_prices(
        this,
        ticker: str,
        interval: Literal["minute", "day", "week", "month", "year"],
        interval_multiplier: int,
        start_date: str,
        end_date: str,
    ) -> dict:
        """Fetch historical price data from Yahoo Finance."""
        stock = this._get_ticker(ticker)

        # Map interval to yfinance format
        interval_map = {
            "minute": f"{interval_multiplier}m",
            "day": f"{interval_multiplier}d",
            "week": f"{interval_multiplier}wk",
            "month": f"{interval_multiplier}mo",
            "year": "1y",  # yfinance doesn't support multi-year intervals
        }

        yf_interval = interval_map.get(interval, "1d")

        # Fetch data
        hist = stock.history(start=start_date, end=end_date, interval=yf_interval)

        if hist.empty:
            return []

        # Convert to list of dicts
        prices = []
        for date, row in hist.iterrows():
            price = {
                "date": (
                    date.strftime("%Y-%m-%d")
                    if hasattr(date, "strftime")
                    else str(date)
                ),
                "open": float(row["Open"]) if "Open" in row else None,
                "high": float(row["High"]) if "High" in row else None,
                "low": float(row["Low"]) if "Low" in row else None,
                "close": float(row["Close"]) if "Close" in row else None,
                "volume": int(row["Volume"]) if "Volume" in row else None,
            }
            prices.append(price)

        return prices

    def get_news(
        this,
        ticker: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 5,
    ) -> dict:
        """Fetch news from Yahoo Finance."""
        stock = this._get_ticker(ticker)

        try:
            news = stock.news
        except:
            news = []

        if not news:
            return []

        # Filter by date if provided
        filtered_news = []
        for article in news[:limit]:
            article_data = {
                "title": article.get("title"),
                "publisher": article.get("publisher"),
                "link": article.get("link"),
                "published_date": (
                    datetime.fromtimestamp(
                        article.get("providerPublishTime", 0)
                    ).strftime("%Y-%m-%d")
                    if article.get("providerPublishTime")
                    else None
                ),
                "type": article.get("type"),
            }

            # Apply date filters if provided
            if start_date or end_date:
                pub_date = article_data.get("published_date")
                if pub_date:
                    if start_date and pub_date < start_date:
                        continue
                    if end_date and pub_date > end_date:
                        continue

            filtered_news.append(article_data)

        return filtered_news[:limit]

    def get_financial_metrics_snapshot(this, ticker: str) -> dict:
        """Fetch current financial metrics from Yahoo Finance."""
        stock = this._get_ticker(ticker)
        info = stock.info

        return {
            "ticker": ticker,
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "peg_ratio": info.get("pegRatio"),
            "price_to_book": info.get("priceToBook"),
            "price_to_sales": info.get("priceToSalesTrailing12Months"),
            "ev_to_revenue": info.get("enterpriseToRevenue"),
            "ev_to_ebitda": info.get("enterpriseToEbitda"),
            "dividend_yield": info.get("dividendYield"),
            "beta": info.get("beta"),
            "profit_margin": info.get("profitMargins"),
            "operating_margin": info.get("operatingMargins"),
            "return_on_assets": info.get("returnOnAssets"),
            "return_on_equity": info.get("returnOnEquity"),
            "revenue_per_share": info.get("revenuePerShare"),
            "book_value": info.get("bookValue"),
            "debt_to_equity": info.get("debtToEquity"),
            "current_ratio": info.get("currentRatio"),
            "quick_ratio": info.get("quickRatio"),
        }

    def get_financial_metrics(
        this,
        ticker: str,
        period: Literal["annual", "quarterly", "ttm"] = "ttm",
        limit: int = 4,
        **kwargs,
    ) -> dict:
        """
        Fetch historical financial metrics.
        Note: Yahoo Finance provides limited historical metrics,
        mostly in the current snapshot.
        """
        # For historical metrics, we'd need to calculate from financial statements
        # This is a simplified version returning current snapshot
        return [this.get_financial_metrics_snapshot(ticker)]
