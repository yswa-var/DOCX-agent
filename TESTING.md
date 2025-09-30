# DOCX Agent Testing Guide

## Overview

This DOCX Agent uses **LangGraph + OpenAI** to provide intelligent CRUD operations on Word documents through natural language.

## Architecture

```
User Query (Natural Language)
        ↓
    OpenAI LLM (Reasoning)
        ↓
    Tool Selection & Parameter Extraction
        ↓
    ┌─────────────────────────────────┐
    │  Agent Tools (in tools.py)      │
    ├─────────────────────────────────┤
    │  • get_paragraph(anchor)        │
    │  • update_paragraph(anchor, text)│
    │  • get_document_outline()       │
    │  • search_document(query)       │
    └─────────────────────────────────┘
        ↓
    ┌─────────────────────────────────┐
    │  DOCX Manager (docx_manager.py) │
    ├─────────────────────────────────┤
    │  • Index management             │
    │  • Read operations              │
    │  • Update operations            │
    └─────────────────────────────────┘
        ↓
    ┌─────────────────────────────────┐
    │  DOCX Indexer (docx_indexer.py) │
    ├─────────────────────────────────┤
    │  • Parse DOCX structure         │
    │  • Build anchor mappings        │
    │  • Generate breadcrumbs         │
    │  • Detect heading hierarchy     │
    └─────────────────────────────────┘
        ↓
    DOCX File (docx2python + python-docx)
```

## Why OpenAI for CRUD?

**YES**, we use OpenAI (or any LLM) to make CRUD operations more professional:

### Benefits:

1. **Natural Language Interface** 🗣️
   - No need to know exact anchor positions
   - "Update section 2.1" instead of `update_paragraph(['body', 0, 0, 0, 15], ...)`

2. **Intelligent Query Understanding** 🧠
   - "Find all pricing sections" → Automatically searches and filters
   - "Update the introduction" → Finds the right paragraph without coordinates

3. **Context-Aware Operations** 🎯
   - "Change CPX to CompanyX in the team section" → Scoped updates
   - "What does the contract say about payments?" → Semantic search

4. **Multi-Step Reasoning** 🔗
   - Complex queries broken into tool calls
   - "Compare sections 3 and 4" → Multiple reads + analysis

5. **Error Handling & Validation** ✅
   - LLM validates parameters before calling tools
   - Provides helpful error messages

### Example:

**Without LLM (Manual):**
```python
# You need to know the exact structure
anchor = ["body", 2, 5, 0, 12]
update_paragraph(anchor, "New text")
```

**With LLM (Professional):**
```
User: "Update the pricing section to include 20% discount"

LLM reasoning:
1. Search for "pricing" → get anchor
2. Get current text → understand structure
3. Modify text with 20% discount
4. Call update_paragraph(anchor, new_text)
5. Return success message
```

## Quick Start

### 1. Install Dependencies

```bash
cd /Users/yash/Documents/rfp/DOCX-agent
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Test Basic Operations

```bash
python test_agent.py
```

This will:
- ✅ Index the sample DOCX file
- ✅ Test all CRUD operations
- ✅ Generate `document_index.json`
- ✅ Show example prompts

### 3. Run with LangGraph Studio

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="sk-..."

# Start LangGraph dev server
cd main
langgraph dev
```

Then open http://localhost:8000 in your browser.

### 4. Test Natural Language Queries

Try these prompts in LangGraph Studio:

#### 📖 Read Operations
```
- "Show me the document outline"
- "What's in section 2.1?"
- "Find all mentions of CPX"
- "What does the pricing section say?"
```

#### ✏️ Update Operations
```
- "Change the title to 'Updated RFP Response'"
- "Update section 2.1 to say 'Company Profile'"
- "Add 'Experienced' before 'Team' in section 6"
```

#### 🔍 Search Operations
```
- "Find paragraphs about implementation"
- "Show me all headings"
- "Where is the risk assessment section?"
```

#### 🎯 Complex Operations
```
- "Find the pricing section and update it to include a 10% discount"
- "List all subsections under 'About CPX'"
- "What's the breadcrumb path to the timeline section?"
```

## Anchor System

Every paragraph has a unique anchor:

```json
{
  "anchor": ["body", 0, 0, 0, 5],
  "breadcrumb": "RFP PROPOSAL RESPONSE > Table of Contents",
  "style": "Heading 2",
  "text": "Table of Contents",
  "level": 2
}
```

**Anchor Format:** `["body", table_idx, row_idx, col_idx, par_idx]`

- `table_idx`: Table/section in document
- `row_idx`: Row within table
- `col_idx`: Column within row
- `par_idx`: Paragraph within column

## Document Index Structure

The indexer generates a JSON with:

```json
[
  {
    "anchor": ["body", 0, 0, 0, 0],
    "breadcrumb": "RFP PROPOSAL RESPONSE",
    "style": "Heading 1",
    "text": "RFP PROPOSAL RESPONSE",
    "level": 1
  },
  {
    "anchor": ["body", 0, 0, 0, 5],
    "breadcrumb": "Table of Contents",
    "style": "Heading 2",
    "text": "Table of Contents",
    "level": 2
  }
]
```

## Available Tools

### 1. `get_paragraph(anchor: List[Any])`
Get a specific paragraph by its anchor.

**Example:**
```python
result = await get_paragraph(["body", 0, 0, 0, 5])
# Returns: {"anchor": [...], "text": "...", "breadcrumb": "...", "style": "..."}
```

### 2. `update_paragraph(anchor: List[Any], new_text: str)`
Update a paragraph's content.

**Example:**
```python
result = await update_paragraph(["body", 0, 0, 0, 5], "New Title")
# Returns: {"success": True, "message": "Paragraph updated successfully"}
```

### 3. `get_document_outline()`
Get all headings in the document.

**Example:**
```python
result = await get_document_outline()
# Returns: {"headings": [...], "count": 36}
```

### 4. `search_document(query: str, case_sensitive: bool = False)`
Search for text in the document.

**Example:**
```python
result = await search_document("CPX")
# Returns: {"matches": [...], "count": 15}
```

## Configuration

Edit the default document path in `docx_manager.py`:

```python
def get_docx_manager(docx_path: Optional[str] = None) -> DocxManager:
    if docx_path is None:
        docx_path = "/path/to/your/document.docx"  # Change this
    return DocxManager(docx_path)
```

## Features

✅ **Depth-4 DOCX Parsing** - Full document structure access  
✅ **Anchor-Based Navigation** - Precise paragraph addressing  
✅ **Breadcrumb Trails** - Hierarchical context for each paragraph  
✅ **Heading Detection** - Automatic style recognition  
✅ **Natural Language Interface** - OpenAI-powered queries  
✅ **CRUD Operations** - Read, search, and update content  
✅ **LangGraph Integration** - Agent-based workflows  
✅ **JSON Export** - Structured document index  

## Troubleshooting

### Issue: "Module not found"
```bash
# Make sure you're in the venv and installed dependencies
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: "Cannot find document"
```bash
# Update the path in docx_manager.py or pass it as parameter
```

### Issue: OpenAI API errors
```bash
# Set your API key
export OPENAI_API_KEY="sk-..."

# Or set in main/langgraph.json
```

## Next Steps

1. ✅ Test basic operations: `python test_agent.py`
2. ✅ Run LangGraph: `cd main && langgraph dev`
3. ✅ Try natural language queries in Studio
4. ✅ Customize prompts in `main/src/react_agent/prompts.py`
5. ✅ Add more tools as needed in `tools.py`

## Example Session

```
User: "Show me the document outline"

Agent: 🔍 Using tool: get_document_outline()

Result:
Found 36 headings in the document:
1. RFP PROPOSAL RESPONSE
   2. Table of Contents
   2. 1. Summary
   2. 2. About CPX
   2. 3. Understanding of Requirements
   ...

User: "Update section 2.1 to say 'Company Overview and History'"

Agent: 🔍 Using tool: search_document("2.1")
       📝 Using tool: update_paragraph(...)

Result: ✅ Successfully updated section 2.1!
```

Happy document editing! 🚀
