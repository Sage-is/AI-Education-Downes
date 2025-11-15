from collections.abc import Mapping
from typing import Any

from langchain_core.tools import BaseTool

from downes.tools.education import EDUCATION_TOOLS
from downes.tools.search.searx import searx_search
from downes.tools.search.google import search_google_news


TOOLS: tuple[BaseTool, ...] = (
    *EDUCATION_TOOLS,
    searx_search,
    search_google_news,
)

TOOLS_BY_NAME: dict[str, BaseTool] = {tool.name: tool for tool in TOOLS}


def iter_tools() -> tuple[BaseTool, ...]:
    return TOOLS


def get_tool(name: str) -> BaseTool | None:
    return TOOLS_BY_NAME.get(name)


def invoke_tool(tool: BaseTool, args: Mapping[str, Any]) -> Any:
    if hasattr(tool, "invoke"):
        return tool.invoke(args)
    if hasattr(tool, "run"):
        return tool.run(args)
    if callable(tool):
        try:
            return tool(**args)  # type: ignore[misc]
        except TypeError:
            return tool(args)  # type: ignore[misc]
    raise TypeError(f"Tool {getattr(tool, 'name', tool)} is not callable.")


def call_tool(name: str, args: Mapping[str, Any]) -> Any:
    tool = get_tool(name)
    if tool is None:
        raise KeyError(f"Unknown tool: {name}")
    return invoke_tool(tool, args)
