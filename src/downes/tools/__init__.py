# This file makes the directory a Python package from typing_extensions import Callable
from typing_extensions import Callable

from downes.tools.search.google import search_google_news
from downes.tools.search.searx import searx_search
from downes.tools.education import EDUCATION_TOOLS

TOOLS: list[Callable[..., any]] = [
    search_google_news,
]

# Extend with education-focused tools
TOOLS.extend(EDUCATION_TOOLS)
TOOLS.append(searx_search)
