# MCP Server Quick Start

Get your LangGraph DOCX Agent running as an MCP server in 5 minutes!

## ⚡️ Quick Setup

### 1. Install Dependencies

```bash
cd /Users/yash/Documents/rfp/DOCX-agent/main
pip install -e .
```

### 2. Configure Environment

Create a `.env` file:

```bash
# Required: Choose your LLM provider
OPENAI_API_KEY=your-openai-key
# OR
ANTHROPIC_API_KEY=your-anthropic-key
```

### 3. Start the Server

```bash
./start_mcp_server.sh
```

That's it! Your MCP server is now running at `http://localhost:8123/mcp` 🎉

## 🧪 Test It

```bash
# Run the test suite
python test_mcp_server.py
```

## 🔌 Connect MCP Clients

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "docx_agent": {
      "url": "http://localhost:8123/mcp"
    }
  }
}
```

Restart Claude Desktop and start using:
- "Index my document"
- "Search for 'contract terms'"
- "Update section 2.1"
- "Generate a table of contents"

### Cursor

Add to Cursor MCP settings:

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

## 🛠️ Available Tools

| Tool | Description | Requires Approval |
|------|-------------|-------------------|
| `index_docx` | Index/re-index documents | No |
| `apply_edit` | Update paragraph content | ✅ Yes |
| `update_toc` | Generate table of contents | No |
| `get_paragraph` | Get specific paragraph | No |
| `search_document` | Search document text | No |
| `get_document_outline` | Get heading structure | No |

## 📖 Example Usage

Once connected to an MCP client:

```
User: "Index the master.docx document and show me the structure"
Agent: Uses index_docx → Returns document statistics and outline

User: "Find all mentions of 'pricing'"
Agent: Uses search_document → Returns matching paragraphs with anchors

User: "Update the executive summary to say 'Updated for Q4 2025'"
Agent: Uses search_document → apply_edit → Requests your approval

User: "Create a table of contents"
Agent: Uses update_toc → Returns hierarchical TOC
```

## 🔧 Troubleshooting

### Server won't start?
```bash
# Check if port is in use
lsof -ti:8123 | xargs kill -9

# Reinstall dependencies
pip install -e . --force-reinstall
```

### Can't connect from MCP client?
- Ensure server is running: `curl http://localhost:8123/health`
- Check firewall settings
- Verify the URL in client config

### Tools not working?
- Check `.env` file has valid API keys
- Verify document path in `docx_manager.py`
- Check logs in terminal where server is running

## 📚 More Information

- **Full Setup Guide:** [MCP_SETUP.md](./MCP_SETUP.md)
- **Tool Documentation:** [tools.py](./src/react_agent/tools.py)
- **Agent Logic:** [graph.py](./src/react_agent/graph.py)
- **Testing:** [test_mcp_server.py](./test_mcp_server.py)

## 🚀 Next Steps

1. ✅ Start the server
2. ✅ Test with `test_mcp_server.py`
3. ✅ Connect your MCP client (Claude/Cursor)
4. ✅ Start using natural language to manipulate documents!
5. 🎯 Customize tools in `tools.py` for your use case

---

**Need help?** Check [MCP_SETUP.md](./MCP_SETUP.md) for detailed instructions and troubleshooting.
