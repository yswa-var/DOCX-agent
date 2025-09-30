"""This module provides example tools for web scraping and search functionality.

It includes a basic Tavily search function (as an example)

These tools are intended as free examples to get started. For production use,
consider implementing more robust and specialized tools tailored to your needs.
"""

import asyncio
from typing import Any, Callable, List, Optional, cast

from langchain_tavily import TavilySearch  # type: ignore[import-not-found]
from langgraph.runtime import get_runtime

from react_agent.context import Context
from react_agent.docx_manager import get_docx_manager


async def search(query: str) -> Optional[dict[str, Any]]:
    """Search for general web results.

    This function performs a search using the Tavily search engine, which is designed
    to provide comprehensive, accurate, and trusted results. It's particularly useful
    for answering questions about current events.
    """
    runtime = get_runtime(Context)
    wrapped = TavilySearch(max_results=runtime.context.max_search_results)
    return cast(dict[str, Any], await wrapped.ainvoke({"query": query}))


async def get_paragraph(anchor: List[Any]) -> Optional[dict[str, Any]]:
    """Get a paragraph from the DOCX document by its anchor.
    
    Args:
        anchor: List representing [body, table, row, col, par] position, e.g. ["body", 0, 0, 0, 5]
    """
    manager = get_docx_manager()
    await manager._ensure_index_loaded()
    return manager.get_paragraph(anchor)


async def update_paragraph(anchor: List[Any], new_text: str) -> dict[str, Any]:
    """Update a paragraph in the DOCX document.
    
    Args:
        anchor: List representing [body, table, row, col, par] position, e.g. ["body", 0, 0, 0, 5]
        new_text: New text content for the paragraph
    """
    manager = get_docx_manager()
    await manager._ensure_index_loaded()
    success = await asyncio.to_thread(manager.update_paragraph, anchor, new_text)
    
    if success:
        return {"success": True, "message": "Paragraph updated successfully"}
    else:
        return {"success": False, "message": "Failed to update paragraph"}


async def get_document_outline() -> dict[str, Any]:
    """Get the document outline showing all headings with their structure and metadata."""
    manager = get_docx_manager()
    await manager._ensure_index_loaded()
    outline = manager.get_outline()
    
    return {
        "headings": outline,
        "count": len(outline)
    }


async def search_document(query: str, case_sensitive: bool = False) -> dict[str, Any]:
    """Search for text within the DOCX document and return matching paragraphs with their anchors and metadata.
    
    Args:
        query: Text to search for in the document
        case_sensitive: Whether to match case, defaults to False for case-insensitive search
    """
    manager = get_docx_manager()
    await manager._ensure_index_loaded()
    matches = manager.search(query, case_sensitive)
    
    return {
        "matches": matches,
        "count": len(matches)
    }


TOOLS: List[Callable[..., Any]] = [
    search,
    get_paragraph,
    update_paragraph,
    get_document_outline,
    search_document,
]
