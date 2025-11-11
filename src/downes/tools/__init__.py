# This file makes the directory a Python package from typing_extensions import Callable
from typing_extensions import Callable
from downes.tools.finance.filings import get_filings
from downes.tools.finance.filings import get_10K_filing_items
from downes.tools.finance.filings import get_10Q_filing_items
from downes.tools.finance.filings import get_8K_filing_items
from downes.tools.finance.fundamentals import get_income_statements
from downes.tools.finance.fundamentals import get_balance_sheets
from downes.tools.finance.fundamentals import get_cash_flow_statements
from downes.tools.finance.metrics import get_financial_metrics_snapshot
from downes.tools.finance.metrics import get_financial_metrics
from downes.tools.finance.prices import get_price_snapshot
from downes.tools.finance.prices import get_prices
from downes.tools.finance.news import get_news
from downes.tools.finance.estimates import get_analyst_estimates
from downes.tools.finance.segments import get_segmented_revenues
from downes.tools.search.google import search_google_news

TOOLS: list[Callable[..., any]] = [
    get_income_statements,
    get_balance_sheets,
    get_cash_flow_statements,
    get_10K_filing_items,
    get_10Q_filing_items,
    get_8K_filing_items,
    get_filings,
    get_price_snapshot,
    get_prices,
    get_financial_metrics_snapshot,
    get_financial_metrics,
    get_news,
    get_analyst_estimates,
    get_segmented_revenues,
    search_google_news,
]
