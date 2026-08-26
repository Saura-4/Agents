"""Tavily search integration."""

from clients import tavily_client


def search_web(query: str, max_results: int = 5) -> list[dict]:
    """Return a predictable, small representation of Tavily results."""
    response = tavily_client.search(query=query, search_depth="basic", max_results=max_results)
    return [
        {"id": index, "title": result.get("title", "Untitled result"), "url": result.get("url", ""), "content": result.get("content", "")}
        for index, result in enumerate(response.get("results", []), start=1)
    ]
