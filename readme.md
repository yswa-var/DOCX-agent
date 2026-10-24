# DOCX Agent - AI-Powered Document CRUD Operations

An intelligent document editing system that combines **LangGraph**, **OpenAI**, and **docx2python** to perform CRUD operations on Word documents using natural language.

<img width="864" height="497" alt="Screenshot 2025-09-30 at 7 30 25 PM" src="https://github.com/user-attachments/assets/9817b72a-f468-463f-ab4b-4afd1a814a51" />

## Key Features

- **Natural Language Interface** - Edit documents with plain English
- **Anchor-Based Navigation** - Precise paragraph addressing with depth-4 enumeration
- **Breadcrumb Trails** - Hierarchical context for every paragraph
- **OpenAI-Powered CRUD** - Intelligent operation routing and execution
- **LangGraph Integration** - Agent-based workflows with tool calling
- **JSON Export** - Structured document index with metadata

## Architecture

```
User Natural Language Query
          |
   OpenAI LLM (Reasoning)
          |
   +----------------------------+
   | LangGraph Agent            |
   | (graph.py)                 |
   +----------------------------+
          |
   +----------------------------+
   | Agent Tools                |
   | get_paragraph()            |
   | update_paragraph()         |
   | get_document_outline()     |
   | search_document()          |
   +----------------------------+
          |
   +----------------------------+
   | DOCX Manager               |
   | (Index & Operations)       |
   +----------------------------+
          |
   +----------------------------+
   | DOCX Indexer               |
   | (Structure Parser)         |
   +----------------------------+
          |
      DOCX File
```

## Installation

```bash
# Clone and setup
cd /Users/yash/Documents/rfp/DOCX-agent
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

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
