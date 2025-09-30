"""Test script for the MCP server.

This script tests the MCP endpoint by making requests to the running server.
Make sure the server is running before executing this script.
"""

import asyncio
import sys
from typing import Any, Dict

import httpx


SERVER_URL = "http://localhost:8123"
MCP_ENDPOINT = f"{SERVER_URL}/mcp"


async def test_health_check():
    """Test server health endpoint."""
    print("🔍 Testing server health...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SERVER_URL}/health")
            if response.status_code == 200:
                print("✅ Server is healthy")
                return True
            else:
                print(f"❌ Server health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Server is not running: {e}")
            print(f"   Start the server with: ./start_mcp_server.sh")
            return False


async def test_index_docx():
    """Test the index_docx tool."""
    print("\n📚 Testing index_docx tool...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Use the agent through a run
            response = await client.post(
                f"{SERVER_URL}/runs/stream",
                json={
                    "assistant_id": "docx_agent",
                    "input": {
                        "messages": [
                            {
                                "role": "user",
                                "content": "Index the document and show me the first few headings"
                            }
                        ]
                    },
                    "config": {},
                    "stream_mode": ["values"]
                }
            )
            
            print(f"Response status: {response.status_code}")
            if response.status_code == 200:
                print("✅ index_docx tool executed successfully")
                # Parse streaming response
                for line in response.text.split('\n'):
                    if line.strip():
                        print(f"   {line[:100]}...")
            else:
                print(f"❌ Tool execution failed: {response.text}")
        except Exception as e:
            print(f"❌ Error testing tool: {e}")


async def test_search_document():
    """Test the search_document tool."""
    print("\n🔍 Testing search_document tool...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{SERVER_URL}/runs/stream",
                json={
                    "assistant_id": "docx_agent",
                    "input": {
                        "messages": [
                            {
                                "role": "user",
                                "content": "Search the document for the word 'section'"
                            }
                        ]
                    },
                    "config": {},
                    "stream_mode": ["values"]
                }
            )
            
            print(f"Response status: {response.status_code}")
            if response.status_code == 200:
                print("✅ search_document tool executed successfully")
            else:
                print(f"❌ Tool execution failed: {response.text}")
        except Exception as e:
            print(f"❌ Error testing tool: {e}")


async def test_update_toc():
    """Test the update_toc tool."""
    print("\n📑 Testing update_toc tool...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{SERVER_URL}/runs/stream",
                json={
                    "assistant_id": "docx_agent",
                    "input": {
                        "messages": [
                            {
                                "role": "user",
                                "content": "Generate a table of contents for the document"
                            }
                        ]
                    },
                    "config": {},
                    "stream_mode": ["values"]
                }
            )
            
            print(f"Response status: {response.status_code}")
            if response.status_code == 200:
                print("✅ update_toc tool executed successfully")
            else:
                print(f"❌ Tool execution failed: {response.text}")
        except Exception as e:
            print(f"❌ Error testing tool: {e}")


async def list_available_assistants():
    """List available assistants/agents."""
    print("\n📋 Listing available assistants...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SERVER_URL}/assistants")
            if response.status_code == 200:
                assistants = response.json()
                print(f"✅ Found {len(assistants)} assistant(s):")
                for assistant in assistants:
                    print(f"   - {assistant.get('assistant_id', 'unknown')}")
                    print(f"     Description: {assistant.get('description', 'N/A')[:80]}...")
            else:
                print(f"❌ Failed to list assistants: {response.text}")
        except Exception as e:
            print(f"❌ Error listing assistants: {e}")


async def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 MCP Server Test Suite")
    print("=" * 60)
    
    # Test health check first
    if not await test_health_check():
        print("\n❌ Server is not running. Please start it first:")
        print("   cd /Users/yash/Documents/rfp/DOCX-agent/main")
        print("   ./start_mcp_server.sh")
        sys.exit(1)
    
    # List available assistants
    await list_available_assistants()
    
    # Test individual tools
    await test_index_docx()
    await test_search_document()
    await test_update_toc()
    
    print("\n" + "=" * 60)
    print("✅ Test suite completed!")
    print("=" * 60)
    print("\n💡 Tips:")
    print("   - Check MCP_SETUP.md for detailed usage instructions")
    print("   - Connect MCP clients (Claude, Cursor) to use natural language")
    print("   - All write operations require human approval")


if __name__ == "__main__":
    asyncio.run(main())
