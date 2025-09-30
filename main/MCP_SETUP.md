# MCP Server Setup Guide

This guide explains how to set up and run your LangGraph DOCX agent as an MCP (Model Context Protocol) server.

## What is MCP?

Model Context Protocol (MCP) is an open standard that allows AI models to interact with external tools and services. By running your LangGraph agent as an MCP server, you can expose your DOCX manipulation tools to any MCP-compatible client (like Claude Desktop, Cursor, or custom AI applications).

## Prerequisites

1. **Python 3.11+** installed
2. **Required dependencies** (installed automatically with the project)
3. **Environment variables** configured in `.env` file

## Installation

1. **Install dependencies:**

```bash
cd /Users/yash/Documents/rfp/DOCX-agent/main
pip install -e .
```

This will install all required packages including:
- `langgraph-api>=0.2.3` (MCP support)
- `langgraph-sdk>=0.1.61` (MCP client SDK)
- All other project dependencies

## Configuration

The MCP server is configured in `langgraph.json`:

```json
{
  "graphs": {
    "docx_agent": {
      "path": "./src/react_agent/graph.py:graph",
      "description": "AI-powered DOCX document agent..."
    }
  }
}
```

## Running the MCP Server

### Option 1: Using LangGraph CLI (Recommended)

```bash
# Start the MCP server with LangGraph CLI
langgraph dev --host 0.0.0.0 --port 8123
```

The server will start and expose:
- **MCP endpoint:** `http://localhost:8123/mcp`
- **API endpoint:** `http://localhost:8123`
- **Studio UI:** Available if using LangGraph Studio

### Option 2: Production Deployment

```bash
# For production, use:
langgraph up --host 0.0.0.0 --port 8123
```

## Exposed Tools

The following tools are available via the MCP endpoint:

### 1. `index_docx`
**Description:** Index or re-index a DOCX document to create structured navigation.

**Parameters:**
- `docx_path` (optional): Path to DOCX file
- `export_json` (optional): Whether to export index to JSON

**Returns:** Index statistics and document structure

### 2. `apply_edit`
**Description:** Apply an edit to a specific paragraph in the document.

**Parameters:**
- `anchor`: List representing paragraph position, e.g., `["body", 0, 0, 0, 5]`
- `new_text`: New text content for the paragraph

**Returns:** Success status and edit confirmation

**Note:** Requires human approval for security.

### 3. `update_toc`
**Description:** Update the Table of Contents based on document headings.

**Parameters:** None

**Returns:** Generated TOC structure with all entries

### 4. `get_paragraph`
**Description:** Get a specific paragraph by its anchor.

**Parameters:**
- `anchor`: List representing paragraph position

**Returns:** Paragraph information with metadata

### 5. `search_document`
**Description:** Search for text within the document.

**Parameters:**
- `query`: Search text
- `case_sensitive` (optional): Whether to match case (default: false)

**Returns:** Matching paragraphs with anchors and metadata

### 6. `get_document_outline`
**Description:** Get document outline with all headings.

**Parameters:** None

**Returns:** Complete heading hierarchy

## Connecting MCP Clients

### Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "docx_agent": {
      "url": "http://localhost:8123/mcp"
    }
  }
}
```

### Cursor

Add to your Cursor MCP settings:

```json
{
  "mcp": {
    "servers": {
      "docx_agent": {
        "url": "http://localhost:8123/mcp"
      }
    }
  }
}
```

### Custom MCP Client

```python
from langgraph_sdk import get_client

client = get_client(url="http://localhost:8123")

# Use the agent as a tool
result = await client.runs.stream(
    thread_id="my-thread",
    assistant_id="docx_agent",
    input={"messages": [{"role": "user", "content": "Index the document"}]}
)
```

## Testing the MCP Server

### 1. Check Server Health

```bash
curl http://localhost:8123/health
```

### 2. List Available Tools

```bash
curl http://localhost:8123/mcp/list_tools
```

### 3. Invoke a Tool

```python
import requests

response = requests.post(
    "http://localhost:8123/mcp/invoke_tool",
    json={
        "tool_name": "index_docx",
        "arguments": {
            "export_json": True
        }
    }
)

print(response.json())
```

## Environment Variables

Create a `.env` file with:

```bash
# Required: Choose your LLM provider
OPENAI_API_KEY=your-openai-key
# OR
ANTHROPIC_API_KEY=your-anthropic-key

# Optional: Document path (defaults to response/master.docx)
DOCX_PATH=/path/to/your/document.docx

# Optional: Server configuration
HOST=0.0.0.0
PORT=8123
```

## Human Approval for Write Operations

The agent requires human approval for write operations (`apply_edit`). When running:

1. **In LangGraph Studio:** Approval prompts appear in the UI
2. **Via API:** Use the interrupt system to handle approvals
3. **Production:** Implement custom approval workflows

To disable approval (not recommended):

```python
# In graph.py, modify WRITE_TOOLS
WRITE_TOOLS = set()  # Empty set = no approval required
```

## Troubleshooting

### Port Already in Use

```bash
# Kill the process using port 8123
lsof -ti:8123 | xargs kill -9

# Or use a different port
langgraph dev --port 8124
```

### Import Errors

```bash
# Reinstall dependencies
pip install -e . --force-reinstall
```

### MCP Endpoint Not Found

Ensure you have the correct versions:

```bash
pip install "langgraph-api>=0.2.3" "langgraph-sdk>=0.1.61" --upgrade
```

## Security Considerations

1. **Authentication:** Add authentication for production deployments
2. **Network:** Use HTTPS in production
3. **Document Access:** Restrict file system access appropriately
4. **Approval Required:** Keep write operations under human approval
5. **Rate Limiting:** Implement rate limits for API endpoints

## Next Steps

1. ✅ Install dependencies
2. ✅ Configure `.env` file
3. ✅ Start the MCP server
4. ✅ Test with curl or Python
5. ✅ Connect your MCP client
6. ✅ Start using natural language to manipulate DOCX files!

## Support

For issues or questions:
- Check the [LangGraph MCP documentation](https://langchain-ai.github.io/langgraph/concepts/mcp/)
- Review logs in your terminal
- Ensure all dependencies are up to date

## Example Usage

Once the server is running, you can use natural language with any connected MCP client:

```
User: "Index the master.docx document"
Agent: [Uses index_docx tool]

User: "Find all paragraphs mentioning 'contract terms'"
Agent: [Uses search_document tool]

User: "Update section 2.1 to say 'Updated Company Profile'"
Agent: [Uses search_document → apply_edit → requests approval]

User: "Generate a table of contents"
Agent: [Uses update_toc tool]
```

The agent intelligently selects and chains tools to accomplish complex tasks!
