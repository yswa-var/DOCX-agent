#!/usr/bin/env python3
"""Test script for DOCX Agent - demonstrates CRUD operations via LangGraph."""

import asyncio
import json
from react_agent.docx_manager import get_docx_manager


async def test_basic_operations():
    """Test basic DOCX operations without the agent."""
    print("=" * 80)
    print("TESTING BASIC DOCX OPERATIONS")
    print("=" * 80)
    
    # Initialize manager
    manager = get_docx_manager("/Users/yash/Documents/rfp/DOCX-agent/response/master.docx")
    
    # Test 1: Get document outline
    print("\n1. GET DOCUMENT OUTLINE")
    print("-" * 80)
    outline = manager.get_outline()
    print(f"Found {len(outline)} headings:\n")
    for heading in outline[:10]:
        indent = "  " * (heading['level'] - 1)
        print(f"{indent}- [{heading['style']}] {heading['text'][:60]}")
        print(f"{indent}  Anchor: {heading['anchor']}")
    
    # Test 2: Get specific paragraph
    print("\n\n2. GET SPECIFIC PARAGRAPH")
    print("-" * 80)
    anchor = ["body", 0, 0, 0, 5]  # Table of Contents heading
    para = manager.get_paragraph(anchor)
    if para:
        print(f"Anchor: {para['anchor']}")
        print(f"Breadcrumb: {para['breadcrumb']}")
        print(f"Style: {para['style']}")
        print(f"Text: {para['text']}")
    
    # Test 3: Search document
    print("\n\n3. SEARCH DOCUMENT")
    print("-" * 80)
    results = manager.search("CPX")
    print(f"Found {len(results)} matches for 'CPX':\n")
    for i, result in enumerate(results[:5], 1):
        print(f"{i}. {result['text'][:80]}...")
        print(f"   Anchor: {result['anchor']}")
        print(f"   Breadcrumb: {result['breadcrumb']}\n")
    
    # Test 4: Get all paragraphs
    print("\n\n4. GET ALL PARAGRAPHS")
    print("-" * 80)
    all_paras = manager.get_all_paragraphs()
    print(f"Total paragraphs in document: {len(all_paras)}")
    
    # Export full index
    print("\n\n5. EXPORT INDEX")
    print("-" * 80)
    manager.export_index("document_index.json")
    print("✓ Exported full index to: document_index.json")


async def test_tools():
    """Test the agent tools directly."""
    print("\n\n" + "=" * 80)
    print("TESTING AGENT TOOLS")
    print("=" * 80)
    
    from react_agent.tools import (
        get_paragraph,
        get_document_outline,
        search_document,
        update_paragraph
    )
    
    # Test get_document_outline
    print("\n1. TOOL: get_document_outline()")
    print("-" * 80)
    result = await get_document_outline()
    print(f"Headings found: {result['count']}")
    print(f"First 5 headings:")
    for heading in result['headings'][:5]:
        print(f"  - {heading['text'][:60]}")
    
    # Test search_document
    print("\n\n2. TOOL: search_document('implementation')")
    print("-" * 80)
    result = await search_document("implementation")
    print(f"Matches found: {result['count']}")
    for match in result['matches'][:3]:
        print(f"\n  Text: {match['text'][:80]}...")
        print(f"  Anchor: {match['anchor']}")
    
    # Test get_paragraph
    print("\n\n3. TOOL: get_paragraph(['body', 0, 0, 0, 5])")
    print("-" * 80)
    result = await get_paragraph(["body", 0, 0, 0, 5])
    if result:
        print(f"  Text: {result['text']}")
        print(f"  Breadcrumb: {result['breadcrumb']}")
        print(f"  Style: {result['style']}")


def print_agent_test_prompts():
    """Print example prompts to test with the LangGraph agent."""
    print("\n\n" + "=" * 80)
    print("LANGGRAPH AGENT TEST PROMPTS")
    print("=" * 80)
    print("""
These prompts demonstrate how OpenAI (or your configured LLM) interprets
natural language and intelligently calls the appropriate CRUD tools:

📖 READ OPERATIONS (Using get_paragraph, get_document_outline, search_document):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. "Show me the document outline"
   → Agent calls: get_document_outline()

2. "What's in the Table of Contents?"
   → Agent calls: search_document("table of contents")

3. "Find all mentions of CPX in the document"
   → Agent calls: search_document("CPX")

4. "What does section 2.1 say?"
   → Agent searches for "2.1", then calls get_paragraph() with the anchor

5. "Show me all the headings in the document"
   → Agent calls: get_document_outline()

6. "What's the first paragraph about?"
   → Agent calls: get_paragraph(["body", 0, 0, 0, 0])

7. "Find paragraphs about 'implementation'"
   → Agent calls: search_document("implementation")


✏️  UPDATE OPERATIONS (Using update_paragraph):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

8. "Change the title to 'RFP RESPONSE DOCUMENT'"
   → Agent finds title paragraph, calls: update_paragraph(anchor, "RFP RESPONSE DOCUMENT")

9. "Update section 2.1 to say 'Company Overview'"
   → Agent searches for section 2.1, calls: update_paragraph(anchor, "Company Overview")

10. "Replace 'CPX' with 'CompanyX' in the first occurrence"
    → Agent finds first CPX paragraph, calls: update_paragraph(anchor, modified_text)


🔍 COMPLEX OPERATIONS (Multiple tool calls):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

11. "Find the pricing section and tell me what it says"
    → Agent: search_document("pricing") → get_paragraph(anchor) → summarize

12. "Update all sections about 'Team' to include 'Experienced'"
    → Agent: search_document("Team") → multiple update_paragraph() calls

13. "Show me the structure of sections 3 through 5"
    → Agent: get_document_outline() → filter sections 3-5 → format output

14. "What's the breadcrumb for the 'Implementation Plan' section?"
    → Agent: search_document("Implementation Plan") → return breadcrumb info


📊 ANALYTICAL OPERATIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

15. "How many sections are in this document?"
    → Agent: get_document_outline() → count top-level headings

16. "List all subsections under 'About CPX'"
    → Agent: get_document_outline() → filter by breadcrumb

17. "Find paragraphs that mention both 'risk' and 'mitigation'"
    → Agent: search_document("risk") → search_document("mitigation") → intersect


🎯 HOW IT WORKS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The LLM (OpenAI/Claude) acts as an intelligent router that:
1. ✅ Understands natural language queries
2. ✅ Decides which tool(s) to call
3. ✅ Extracts parameters from context
4. ✅ Chains multiple tool calls for complex operations
5. ✅ Formats results in human-readable format

Example flow for "Update section 2.1 title":
  User Query → LLM analyzes → Calls search_document("2.1") 
  → Gets anchor → Calls update_paragraph(anchor, new_text)
  → Returns success message


To test with LangGraph:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Set your OpenAI API key:
   export OPENAI_API_KEY="your-key-here"

2. Run LangGraph:
   cd main
   langgraph dev

3. Open LangGraph Studio (http://localhost:8000)

4. Enter any of the above prompts in the chat interface

5. Watch the agent intelligently call the DOCX tools!
""")


async def main():
    """Run all tests."""
    try:
        # Test basic operations
        await test_basic_operations()
        
        # Test tools directly
        await test_tools()
        
        # Print agent test prompts
        print_agent_test_prompts()
        
        print("\n\n✅ All tests completed successfully!\n")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
