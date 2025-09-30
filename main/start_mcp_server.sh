#!/bin/bash

# Minimal LangGraph MCP Server startup script

set -e

echo "🚀 Starting LangGraph MCP Server..."

# Check for .env and langgraph.json
if [ ! -f .env ]; then
    echo "❌ .env file not found! Please create it with your OpenAI API key."
    exit 1
fi

if [ ! -f langgraph.json ]; then
    echo "❌ langgraph.json not found! Please create it or copy from your repo."
    exit 1
fi

# Load environment variables from .env
echo "📋 Loading environment variables..."
set -a
source .env
set +a

# Verify API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY not found in .env file!"
    exit 1
fi

echo "✅ Environment loaded successfully"

# Start LangGraph dev server (matching your manual run)
exec langgraph dev --config langgraph.json --host 127.0.0.1 --port 2024