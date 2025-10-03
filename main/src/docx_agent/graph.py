"""DOCX Agent graph definition for document manipulation workflows.

This module provides a self-contained graph definition for DOCX document
editing and manipulation operations, making it importable anywhere.
"""

from langgraph.graph import StateGraph

from react_agent.state import State, InputState
from react_agent.context import Context
from .nodes import (
    docx_logic, 
    docx_tools, 
    approval_node, 
    route_docx_output, 
    route_docx_approval
)


def build_docx_graph() -> StateGraph:
    """Build and return the DOCX agent graph.
    
    This function creates a StateGraph configured for DOCX document
    manipulation workflows with approval flow for write operations.
    
    Returns:
        StateGraph: Compiled graph for DOCX document operations
    """
    # Create the graph builder
    builder = StateGraph(State, input_schema=InputState, context_schema=Context)

    # Add DOCX-specific nodes
    builder.add_node("docx_logic", docx_logic)
    builder.add_node("approval_node", approval_node)
    builder.add_node("docx_tools", docx_tools())

    # Set the entrypoint as docx_logic
    builder.add_edge("__start__", "docx_logic")

    # Add conditional edges for routing
    builder.add_conditional_edges(
        "docx_logic",
        route_docx_output,
    )

    builder.add_conditional_edges(
        "approval_node",
        route_docx_approval,
    )

    # Create a cycle: after using tools, return to docx_logic
    builder.add_edge("docx_tools", "docx_logic")

    # Compile and return the graph
    return builder.compile(name="DOCX Agent")
