# DOCX Agent - AI-Powered Document CRUD Operations

An intelligent document editing system that combines **LangGraph**, **OpenAI**, and **docx2python** to perform CRUD operations on Word documents using natural language.

## 🎯 Key Features

- ✅ **Natural Language Interface** - Edit documents with plain English
- ✅ **Anchor-Based Navigation** - Precise paragraph addressing with depth-4 enumeration
- ✅ **Breadcrumb Trails** - Hierarchical context for every paragraph
- ✅ **OpenAI-Powered CRUD** - Intelligent operation routing and execution
- ✅ **LangGraph Integration** - Agent-based workflows with tool calling
- ✅ **JSON Export** - Structured document index with metadata

## 🏗️ Architecture

```
User Natural Language Query
          ↓
   OpenAI LLM (Reasoning)
          ↓
   ┌──────────────────────────┐
   │   LangGraph Agent        │
   │   (graph.py)             │
   └──────────────────────────┘
          ↓
   ┌──────────────────────────┐
   │   Agent Tools            │
   │   • get_paragraph()      │
   │   • update_paragraph()   │
   │   • get_document_outline()│
   │   • search_document()    │
   └──────────────────────────┘
          ↓
   ┌──────────────────────────┐
   │   DOCX Manager           │
   │   (Index & Operations)   │
   └──────────────────────────┘
          ↓
   ┌──────────────────────────┐
   │   DOCX Indexer           │
   │   (Structure Parser)     │
   └──────────────────────────┘
          ↓
      DOCX File
```

## 📦 Installation

```bash
# Clone and setup
cd /Users/yash/Documents/rfp/DOCX-agent
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 🚀 Quick Start

### 1. Test Basic Operations

```bash
python test_agent.py
```

This will:
- Index the sample DOCX file
- Test all CRUD operations
- Generate `document_index.json`
- Display example prompts

### 2. Run with LangGraph

```bash
# Set OpenAI API key
export OPENAI_API_KEY="sk-your-key-here"

# Start LangGraph dev server
cd main
langgraph dev
```

Open http://localhost:8000 in your browser.

### 3. Try Natural Language Queries

**Read Operations:**
```
"Show me the document outline"
"What's in section 2.1?"
"Find all mentions of CPX"
```

**Update Operations:**
```
"Change the title to 'Updated RFP Response'"
"Update section 2.1 to say 'Company Profile'"
```

**Search Operations:**
```
"Find paragraphs about implementation"
"Where is the pricing section?"
```

## 📚 How It Works

### 1. Document Indexing (docx2python)

```python
from docx2python import docx2python

with docx2python("document.docx") as docx:
    pars = docx.body  # depth-4: [table][row][col][par]
    first = pars[0][0][0][0]  # First paragraph
```

### 2. Anchor System

Every paragraph gets a unique anchor:

```json
{
  "anchor": ["body", 0, 0, 0, 5],
  "breadcrumb": "RFP PROPOSAL RESPONSE > Table of Contents",
  "style": "Heading 2",
  "text": "Table of Contents",
  "level": 2
}
```

**Anchor Format:** `["body", table, row, column, paragraph]`

### 3. OpenAI Integration

The LLM acts as an intelligent router:

```
User: "Update the pricing section to include 20% discount"

OpenAI reasoning:
1. 🔍 Search for "pricing" → find anchor
2. 📖 Get current text → understand context
3. ✏️  Modify text with discount
4. 💾 Call update_paragraph(anchor, new_text)
5. ✅ Return success message
```

### 4. Agent Tools

Four core tools in `tools.py`:

```python
# READ
await get_paragraph(["body", 0, 0, 0, 5])
await get_document_outline()
await search_document("CPX")

# UPDATE
await update_paragraph(["body", 0, 0, 0, 5], "New text")
```

## 💡 Why OpenAI for CRUD?

### Traditional Approach ❌
```python
# Manual, error-prone
anchor = ["body", 2, 5, 0, 12]
update_paragraph(anchor, "New text")  # How do you know the anchor?
```

### AI-Powered Approach ✅
```
"Update the introduction paragraph"
→ AI finds it, validates context, updates correctly
```

### Benefits:

1. **No Manual Anchor Lookup** - AI finds the right paragraph
2. **Context Understanding** - "pricing section" vs "first pricing mention"
3. **Multi-Step Operations** - "Compare sections 3 and 4"
4. **Error Prevention** - Validates before updating
5. **Natural Language** - "Change X to Y in section Z"

## 📖 API Reference

### DocxIndexer

```python
from react_agent.docx_indexer import DocxIndexer

indexer = DocxIndexer("document.docx")
paragraphs = indexer.index()
outline = indexer.get_outline()
matches = indexer.find_by_text("search term")
indexer.save_index("output.json")
```

### DocxManager

```python
from react_agent.docx_manager import get_docx_manager

manager = get_docx_manager("document.docx")
para = manager.get_paragraph(["body", 0, 0, 0, 5])
outline = manager.get_outline()
results = manager.search("query")
manager.update_paragraph(anchor, "new text")
```

### Agent Tools

```python
from react_agent.tools import (
    get_paragraph,
    update_paragraph,
    get_document_outline,
    search_document
)

# All tools are async
result = await get_document_outline()
```

## 🧪 Testing

### Run All Tests
```bash
python test_agent.py
```

### Test Individual Components
```bash
# Index a document
python main/src/react_agent/docx_indexer.py response/master.docx output.json

# Test manager
python -c "
from react_agent.docx_manager import get_docx_manager
manager = get_docx_manager('response/master.docx')
print(f'Found {len(manager.get_all_paragraphs())} paragraphs')
"
```

## 📝 Example Prompts

See [TESTING.md](TESTING.md) for comprehensive prompt examples.

**Simple Queries:**
- "Show me the outline"
- "What's in section 3?"
- "Find 'implementation'"

**Complex Queries:**
- "Update all pricing sections to include 15% discount"
- "Show me the breadcrumb for the team section"
- "List all subsections under 'About CPX'"

## 🛠️ Configuration

### Change Default Document

Edit `main/src/react_agent/docx_manager.py`:

```python
def get_docx_manager(docx_path: Optional[str] = None) -> DocxManager:
    if docx_path is None:
        docx_path = "/path/to/your/default.docx"  # Change here
    return DocxManager(docx_path)
```

### Configure LLM

Edit `main/langgraph.json` or set environment variables:

```bash
export OPENAI_API_KEY="sk-..."
export OPENAI_MODEL="gpt-4"
```

### Customize System Prompt

Edit `main/src/react_agent/prompts.py`:

```python
DEFAULT_SYSTEM_PROMPT = """
Your custom instructions here...
"""
```

## 📁 Project Structure

```
DOCX-agent/
├── main/
│   └── src/
│       └── react_agent/
│           ├── docx_indexer.py    # DOCX structure parser
│           ├── docx_manager.py    # Document operations
│           ├── tools.py           # LangGraph agent tools
│           ├── graph.py           # Agent graph definition
│           ├── state.py           # Agent state
│           └── prompts.py         # System prompts
├── response/
│   └── master.docx                # Sample document
├── test_agent.py                  # Comprehensive tests
├── TESTING.md                     # Testing guide
├── README.md                      # This file
└── requirements.txt               # Python dependencies
```

## 🔧 Dependencies

- **docx2python** - Parse DOCX structure (depth-4)
- **python-docx** - Edit DOCX content
- **langgraph** - Agent orchestration
- **langchain** - LLM integration
- **openai** - GPT-4 API

## 📊 Output Format

### Index JSON Structure

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

### Tool Response Format

```json
{
  "success": true,
  "message": "Paragraph updated successfully"
}
```

## 🚨 Troubleshooting

### "Module not found" error
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "Cannot access document" error
Update the path in `docx_manager.py` or pass as parameter.

### OpenAI API errors
```bash
export OPENAI_API_KEY="sk-..."
```

## 🎯 Use Cases

- 📄 **RFP Response Automation** - Update proposals with client-specific info
- 📋 **Contract Management** - Search and modify contract terms
- 📊 **Report Generation** - Populate templates with data
- 📝 **Document QA** - Ask questions about document content
- ✏️  **Batch Editing** - Update multiple sections at once

## 🔮 Future Enhancements

- [ ] Support for tables and images
- [ ] Track change history
- [ ] Multi-document operations
- [ ] Export to PDF
- [ ] Template system
- [ ] Collaboration features

## 📄 License

See LICENSE file for details.

## 🤝 Contributing

This is a prototype system. Feel free to extend and customize for your needs!

## 📞 Support

For questions or issues, refer to [TESTING.md](TESTING.md) for detailed examples and troubleshooting.

---

**Built with ❤️ using LangGraph, OpenAI, and docx2python**