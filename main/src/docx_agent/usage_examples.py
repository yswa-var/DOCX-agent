"""Usage examples for the modularized DOCX Agent.

This file demonstrates various ways to use the DOCX agent graph in different contexts.
"""

from typing import Dict, Any
from .graph import build_docx_graph
from react_agent.context import Context
from react_agent.state import InputState


def example_basic_usage():
    """Example 1: Basic usage of the DOCX agent graph."""
    
    # Build the graph
    graph = build_docx_graph()
    
    # Create a simple context
    context = Context(
        model="gpt-4o-mini",  # or your preferred model
        system_prompt="You are a DOCX document editor. Help users read, search, and edit documents."
    )
    
    # Create input state
    input_state = InputState(
        messages=[{"role": "user", "content": "Show me the document outline"}]
    )
    
    print("✅ Basic DOCX agent graph created successfully!")
    print(f"   Graph name: {graph.name}")
    print(f"   Available nodes: {list(graph.nodes.keys())}")
    return graph, context, input_state


def example_custom_context():
    """Example 2: Using the DOCX agent with custom context."""
    
    graph = build_docx_graph()
    
    # Custom context for specific use case
    context = Context(
        model="gpt-4o-mini",
        system_prompt=(
            "You are an expert DOCX document assistant specialized in "
            "technical documentation. Focus on precision and clarity when "
            "editing documents. Always ask for approval before making changes."
        )
    )
    
    print("✅ DOCX agent with custom context created!")
    return graph, context


def example_integration_ready():
    """Example 3: Integration-ready setup for external applications."""
    
    def create_docx_agent(model_name: str = "gpt-4o-mini", 
                         custom_prompt: str = None) -> Dict[str, Any]:
        """Factory function to create a configured DOCX agent.
        
        Args:
            model_name: The LLM model to use
            custom_prompt: Optional custom system prompt
            
        Returns:
            Dictionary with graph, context, and helper functions
        """
        
        # Build the graph
        graph = build_docx_graph()
        
        # Default or custom prompt
        default_prompt = (
            "You are a DOCX document editor. Help users read, search, "
            "and edit documents. Always be helpful and precise."
        )
        
        context = Context(
            model=model_name,
            system_prompt=custom_prompt or default_prompt
        )
        
        def process_request(user_message: str) -> InputState:
            """Helper to create input state from user message."""
            return InputState(
                messages=[{"role": "user", "content": user_message}]
            )
        
        return {
            "graph": graph,
            "context": context,
            "process_request": process_request,
            "graph_name": graph.name,
            "available_nodes": list(graph.nodes.keys())
        }
    
    # Example usage
    agent = create_docx_agent(
        model_name="gpt-4o-mini",
        custom_prompt="You are a legal document editor. Be precise and conservative with changes."
    )
    
    print("✅ Integration-ready DOCX agent created!")
    print(f"   Graph name: {agent['graph_name']}")
    print(f"   Available nodes: {agent['available_nodes']}")
    
    return agent


def main():
    """Run all examples."""
    print("🚀 DOCX Agent Modularization Examples\n")
    
    print("Example 1: Basic Usage")
    example_basic_usage()
    print()
    
    print("Example 2: Custom Context")
    example_custom_context()
    print()
    
    print("Example 3: Integration Ready")
    example_integration_ready()
    print()
    
    print("✅ All examples completed successfully!")
    print("\n📝 The DOCX agent is now modularized and ready for use in any project!")


if __name__ == "__main__":
    main()
