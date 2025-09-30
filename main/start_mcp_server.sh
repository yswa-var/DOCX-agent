#!/bin/bash

# Start MCP Server for LangGraph DOCX Agent
# This script starts the LangGraph server with MCP support

set -e

echo "🚀 Starting LangGraph MCP Server..."
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found"
    echo "Creating .env from .env.example if available..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env file. Please update it with your API keys."
    else
        echo "❌ No .env.example found. Please create a .env file with your API keys."
        exit 1
    fi
fi

# Check if dependencies are installed
echo "📦 Checking dependencies..."
if ! python -c "import langgraph" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -e .
fi

# Set default values
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8123}"

echo ""
echo "📋 Configuration:"
echo "   Host: $HOST"
echo "   Port: $PORT"
echo "   MCP Endpoint: http://$HOST:$PORT/mcp"
echo ""
echo "🔧 Available Tools:"
echo "   - index_docx: Index/re-index DOCX documents"
echo "   - apply_edit: Apply edits to paragraphs (requires approval)"
echo "   - update_toc: Generate table of contents"
echo "   - get_paragraph: Get specific paragraph by anchor"
echo "   - search_document: Search for text in document"
echo "   - get_document_outline: Get document heading structure"
echo ""
echo "📖 For setup instructions, see MCP_SETUP.md"
echo ""
echo "Starting server..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start the LangGraph server
langgraph dev --host "$HOST" --port "$PORT"
