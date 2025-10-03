# DOCX Agent Package

A modularized DOCX document manipulation agent built with LangGraph. This package provides a self-contained, reusable graph definition for DOCX document editing and manipulation workflows.

## Features

- **Modular Design**: Self-contained graph definition that can be imported anywhere
- **Approval Flow**: Built-in human approval for write operations
- **DOCX Tools**: Complete set of tools for document manipulation
- **Flexible Integration**: Easy to integrate into existing applications

## Quick Start

### Basic Usage

```python
from docx_agent.graph import build_docx_graph
from react_agent.context import Context
from react_agent.state import InputState

# Build the DOCX agent graph
graph = build_docx_graph()

# Create context
context = Context(
    model="gpt-4o-mini",
    system_prompt="You are a DOCX document editor."
)

# Create input state
input_state = InputState(
    messages=[{"role": "user", "content": "Show me the document outline"}]
)

# The graph is ready to use with LangGraph runtime
```

### Factory Pattern

```python
from docx_agent.usage_examples import create_docx_agent

# Create a configured agent
agent = create_docx_agent(
    model_name="gpt-4o-mini",
    custom_prompt="You are a legal document editor. Be precise with changes."
)

# Use the agent
user_request = "Search for 'contract' in the document"
input_state = agent["process_request"](user_request)
```

## Architecture

### Graph Structure

The DOCX agent graph consists of the following nodes:

- **`docx_logic`**: Main reasoning node for DOCX operations
- **`docx_tools`**: Tool execution node for document manipulation
- **`approval_node`**: Human approval for write operations

### Node Flow

```
__start__ → docx_logic → [approval_node] → docx_tools → docx_logic
```

The approval node is conditionally executed based on the tools being called.

## Available Tools

The DOCX agent includes the following tools:

- `index_docx`: Index or re-index a DOCX document
- `apply_edit`: Apply edits to specific paragraphs
- `update_toc`: Update the Table of Contents
- `get_paragraph`: Retrieve paragraph information
- `search_document`: Search for text within the document
- `get_document_outline`: Get the document outline

## Integration Examples

### Example 1: Simple Integration

```python
from docx_agent.graph import build_docx_graph

# Build and use the graph
graph = build_docx_graph()
print(f"Graph created: {graph.name}")
```

### Example 2: Custom Context

```python
from docx_agent.graph import build_docx_graph
from react_agent.context import Context

graph = build_docx_graph()
context = Context(
    model="gpt-4o-mini",
    system_prompt="You are an expert technical writer. Focus on clarity and precision."
)
```

### Example 3: External Project Integration

```python
# In your external project
from docx_agent.graph import build_docx_graph

def setup_docx_editor():
    """Setup DOCX editor for your application."""
    return build_docx_graph()

# Use in your application
editor_graph = setup_docx_editor()
```

## File Structure

```
docx_agent/
├── __init__.py          # Package initialization
├── graph.py             # Main graph definition
├── nodes.py             # DOCX-specific nodes
├── example.py           # Basic usage example
├── usage_examples.py    # Comprehensive examples
└── README.md           # This file
```

## Dependencies

The DOCX agent package depends on:

- `langgraph`: For graph-based agent workflows
- `langchain_core`: For message handling
- `react_agent`: For state management and tools

## Approval Flow

Write operations (like `apply_edit`) require human approval:

1. Agent identifies operations needing approval
2. Execution pauses at `approval_node`
3. Human reviews the proposed changes
4. Approval or rejection determines next action

## Error Handling

The DOCX agent includes robust error handling:

- Model response validation
- Tool execution error recovery
- Graceful degradation on failures

## Testing

Run the examples to verify the modularized structure:

```bash
# Basic example
python -m src.docx_agent.example

# Comprehensive examples
python -m src.docx_agent.usage_examples
```

## Contributing

When adding new DOCX functionality:

1. Add new tools to `react_agent.tools`
2. Update approval logic in `nodes.py` if needed
3. Update documentation and examples

## License

This package is part of the DOCX Agent project and follows the same license terms.
