# Migration Summary: Free Data Sources & Flexible LLM Support

## What Changed

This project has been refactored to:
1. **Remove dependency on paid Financial Datasets API** - uses free Yahoo Finance & SEC EDGAR by default
2. **Support any OpenAI-compatible LLM** - works with OpenAI, OpenRouter, Ollama, llama.cpp, and more

### Key Changes

1. **New Provider Architecture**
   - Created an abstract `DataProvider` base class for pluggable data sources
   - Implemented multiple provider backends:
     - **Yahoo Finance** (free) - via yfinance library
     - **SEC EDGAR** (free) - direct SEC API access
     - **Financial Datasets** (optional/paid) - legacy support for existing users

2. **Default Behavior**
   - **No API keys required** for basic functionality
   - Automatically uses Yahoo Finance for prices, statements, metrics, and news
   - Automatically uses SEC EDGAR for filing metadata
   - Falls back to Financial Datasets API only if user provides API key

3. **Updated Dependencies**
   - Added: `yfinance>=0.2.40` (free Yahoo Finance data)
   - Kept: `requests` (for SEC API and optional Financial Datasets)
   - No breaking changes to existing dependencies

4. **Files Modified**
   - `pyproject.toml` - Added yfinance dependency
   - `env.example` - Made Financial Datasets API key optional
   - `README.md` - Updated to reflect free data sources
   - All tool files in `src/downes/tools/finance/`:
     - `fundamentals.py`
     - `prices.py`
     - `news.py`
     - `metrics.py`
     - `filings.py`
     - `estimates.py`
     - `segments.py`

5. **Files Created**
   - `src/downes/tools/finance/providers/` directory with:
     - `base.py` - Abstract provider interface
     - `yahoo_finance.py` - Free Yahoo Finance implementation
     - `sec_edgar.py` - Free SEC EDGAR implementation
     - `financial_datasets.py` - Optional paid provider
     - `config.py` - Provider factory and auto-selection logic
     - `__init__.py` - Package initialization

## Features Now Available for FREE

### Yahoo Finance Provider (No API Key)
- ✅ Real-time stock prices and snapshots
- ✅ Historical price data (OHLCV)
- ✅ Income statements (quarterly & annual)
- ✅ Balance sheets (quarterly & annual)
- ✅ Cash flow statements (quarterly & annual)
- ✅ Financial metrics (P/E, market cap, etc.)
- ✅ Company news

### SEC EDGAR Provider (No API Key)
- ✅ SEC filings metadata (10-K, 10-Q, 8-K)
- ✅ Filing dates and accession numbers

### Optional Paid Features (Financial Datasets API)
- Analyst estimates
- Segmented revenues
- Full text extraction from SEC filings
- Higher rate limits

## How to Use

### Quick Start (Free)
```bash
# Install dependencies
uv sync

# Set only your OpenAI API key
cp env.example .env
# Edit .env and add: OPENAI_API_KEY=your-key

# Run the agent
uv run downes-agent
```

### Advanced: Custom Provider
```python
from downes.tools.finance.providers.config import ProviderFactory

# Auto-select best provider (defaults to free Yahoo Finance)
provider = ProviderFactory.create_provider()

# Or specify provider explicitly
provider = ProviderFactory.create_provider("yahoo")

# Composite provider (Yahoo Finance + SEC EDGAR)
provider = ProviderFactory.get_composite_provider()
```

### For Trading API Integration
To integrate your own trading API (e.g., Interactive Brokers, Alpaca, etc.):

1. Create a new provider class inheriting from `DataProvider`
2. Implement required methods (get_prices, get_income_statements, etc.)
3. Register it in the `ProviderFactory`

Example:
```python
from downes.tools.finance.providers.base import DataProvider

class MyTradingAPIProvider(DataProvider):
    def __init__(this, api_key: str, **kwargs):
        super().__init__(api_key=api_key, **kwargs)
        # Initialize your trading API client
    
    def get_price_snapshot(this, ticker: str) -> dict:
        # Call your trading API
        pass
```

## Testing

Run the test suite to verify everything works:
```bash
uv run python test_providers.py
```

Expected output:
```
✓ Auto-selected provider: YahooFinanceProvider
✓ Price snapshot for AAPL: $XXX.XX
✓ Income statements retrieved: X periods
✓ SEC filings retrieved: X 10-K filings
```

## Backward Compatibility

- Existing code using Financial Datasets API will continue to work
- Simply keep `FINANCIAL_DATASETS_API_KEY` in your `.env` file
- The system will auto-detect and use it
- All tool function signatures remain unchanged

## Benefits

1. **💰 Cost Savings**: No expensive API subscriptions required
2. **🚀 Quick Start**: Get started with just an LLM API key (or run locally!)
3. **🔌 Flexible**: Easy to swap providers or add your own
4. **📊 Comprehensive**: Free data covers 90% of use cases
5. **🔄 Extensible**: Simple interface for adding trading APIs or other sources
6. **🤖 LLM Freedom**: Use any model - cloud or local, paid or free

## LLM Support

The agent now works with **any OpenAI-compatible API**:

### Supported LLM Providers
- ✅ **OpenAI** (GPT-4, GPT-3.5, etc.)
- ✅ **OpenRouter** (Access 100+ models with one key)
- ✅ **Ollama** (100% free local models)
- ✅ **llama.cpp** (100% free local models)
- ✅ **LM Studio** (GUI for local models)
- ✅ **Together.ai** (Fast cloud inference)
- ✅ **Anyscale** (Scalable serving)
- ✅ **Sage.is** (Privacy-focused)
- ✅ Any other OpenAI-compatible endpoint

### Example: Running with Ollama (Free & Local)
```bash
# 1. Install Ollama
curl https://ollama.ai/install.sh | sh

# 2. Pull a model
ollama pull llama3.2

# 3. Configure .env
echo "OPENAI_BASE_URL=http://localhost:11434/v1" >> .env
echo "LLM_MODEL=llama3.2" >> .env
echo "OPENAI_API_KEY=not-needed" >> .env

# 4. Run the agent
uv run downes-agent
```

See `llm-providers.env.example` for more configuration examples.

## What to Tell Your Users

> **Downes is now 100% free to use!** 
> 
> We've migrated from a paid financial data API to free, open-source alternatives (Yahoo Finance & SEC EDGAR). This means you can get started with just an OpenAI API key - no expensive financial data subscriptions required.
> 
> If you need premium features like analyst estimates or full SEC filing text, you can optionally add a Financial Datasets API key, but it's no longer required for basic functionality.

## Migration Path for Existing Users

If you were using Financial Datasets API:
1. **No action required** - it still works as an optional provider
2. To switch to free sources: Simply remove `FINANCIAL_DATASETS_API_KEY` from your `.env`
3. The agent will automatically use Yahoo Finance instead

## Support

- Free providers work out of the box
- For trading API integration, see `DataProvider` base class
- For issues, check the test file: `test_providers.py`
