"""Example usage of the modularized DOCX Agent.

This demonstrates how to import and use the DOCX agent graph in other parts
of the application or in external projects.
"""

from .graph import build_docx_graph


def main():
    """Example of how to use the modularized DOCX agent."""
    
    # Build the DOCX graph
    graph = build_docx_graph()
    
    print("DOCX Agent graph created successfully!")
    print(f"Graph name: {graph.name}")
    print(f"Available nodes: {list(graph.nodes.keys())}")
    
    # The graph is now ready to be used with LangGraph runtime
    # You can invoke it with appropriate state and context


if __name__ == "__main__":
    main()
