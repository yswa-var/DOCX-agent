# 🎯 Test Prompts for DOCX Agent

Quick reference for testing the LangGraph DOCX agent with natural language.

## 🚀 Getting Started

```bash
# 1. Set OpenAI API key
export OPENAI_API_KEY="sk-your-key-here"

# 2. Start LangGraph
cd main
langgraph dev

# 3. Open http://localhost:8000
# 4. Use any prompts below!
```

---

## 📖 READ OPERATIONS

### Simple Reads
```
Show me the document outline

What's in the Table of Contents?

Display all headings

What's the first paragraph?

Show me the document structure
```

### Section-Specific Reads
```
What does section 2.1 say?

Show me section 3 about requirements

What's in the pricing section?

Display the implementation plan

Show me the team and experience section
```

### Search Operations
```
Find all mentions of CPX

Search for "implementation"

Where is the risk assessment?

Find paragraphs about pricing

Show me all references to "timeline"
```

---

## ✏️ UPDATE OPERATIONS

### Simple Updates
```
Change the title to "Updated RFP Response"

Update the document version to 2.0

Change "Generated: 2025-09-27" to today's date
```

### Section Updates
```
Update section 2.1 to say "Company Overview and History"

Change the pricing section title to "Investment Details"

Update the conclusion to say "We look forward to your response"
```

### Content Modifications
```
Add "Experienced" before "Team" in section 6

Replace "CPX" with "CompanyX" in the first occurrence

Update the timeline to show Q2 2025 instead of Q1
```

---

## 🔍 COMPLEX OPERATIONS

### Multi-Step Queries
```
Find the pricing section and tell me what it says

Search for implementation timeline and update it to 6 months

Show me all subsections under "About CPX"

What's the breadcrumb path to the team section?
```

### Analytical Queries
```
How many sections are in this document?

List all subsections under section 3

Compare the structure of sections 4 and 5

Find all headings that mention "Plan"
```

### Contextual Updates
```
Update all pricing sections to include "Subject to negotiation"

Find the risk section and add "Mitigation strategies included"

Change all references to "client" to "valued partner"
```

---

## 📊 METADATA QUERIES

### Anchor Information
```
What's the anchor for the Table of Contents?

Show me the anchor for section 2.1

Get the breadcrumb for the pricing section
```

### Style Detection
```
Show me all Heading 1 paragraphs

List all Heading 2 sections

What style is section 3.1?
```

### Document Stats
```
How many paragraphs are in the document?

Count all the headings

How many times does "CPX" appear?
```

---

## 🎭 EXAMPLE SESSIONS

### Session 1: Document Exploration
```
User: Show me the document outline

Agent: Found 36 headings:
1. RFP PROPOSAL RESPONSE
2. Table of Contents
3. 1. Summary
4. 2. About CPX
...

User: What does section 2.1 say?

Agent: Section 2.1 "CPX Purpose & Value" contains:
[paragraph content]

User: Search for "implementation"

Agent: Found 6 matches...
```

### Session 2: Document Updates
```
User: Update the title to "RFP Response - Final Draft"

Agent: ✓ Successfully updated the title!

User: Change section 2.1 to say "Company Profile"

Agent: ✓ Updated section 2.1!

User: Show me the updated section

Agent: Section 2.1 now reads: "Company Profile"
```

### Session 3: Research and Analysis
```
User: How many sections are in this document?

Agent: The document has 10 main sections (Heading 2)

User: List all subsections under "About CPX"

Agent: Section 2 "About CPX" has 5 subsections:
- 2.1. CPX Purpose & Value
- 2.2. Key Information
- 2.3. Certifications
- 2.4. Organizational Structure
- 2.5. Team Composition

User: What's the breadcrumb for 2.3?

Agent: 2. About CPX > 2.3. Certifications & Accreditations
```

---

## 🧠 How the AI Understands These Prompts

The LLM analyzes each prompt and:

1. **Identifies Intent** - Read, Update, Search, or Analyze
2. **Extracts Parameters** - Section numbers, search terms, new text
3. **Selects Tools** - Which operations to call
4. **Chains Operations** - Multiple steps for complex queries
5. **Formats Output** - Human-readable results

### Example Breakdown:

**Prompt:** "Update section 2.1 to say 'Company Profile'"

```
LLM Reasoning:
1. Intent: UPDATE
2. Target: "section 2.1"
3. New text: "Company Profile"

Tool Calls:
1. search_document("2.1")
   → Finds anchor: ["body", 0, 0, 0, 95]
2. get_paragraph(["body", 0, 0, 0, 95])
   → Verifies current content
3. update_paragraph(["body", 0, 0, 0, 95], "Company Profile")
   → Performs update
4. Return success message
```

---

## 💡 Pro Tips

### 1. Be Specific
❌ "Update the document"
✅ "Update section 2.1 to say 'Company Profile'"

### 2. Use Section Numbers
✅ "Show me section 2.1"
✅ "Update 3.2 to include..."

### 3. Request Verification
```
Update the title, then show me the result
```

### 4. Chain Operations
```
Find the pricing section, then update it to include a 10% discount
```

### 5. Ask for Context
```
What's the breadcrumb for section 4.2?
Show me the anchor for the team section
```

---

## 🎨 Creative Prompts

Try these for fun:

```
Summarize the entire document in one sentence

What are the top 3 sections by word count?

Create a table of contents based on the headings

Which section mentions "timeline" most often?

Show me the document structure as a tree

What's the longest paragraph in the document?
```

---

## ⚡ Quick Commands

**Outline:**
```
outline
show structure
list headings
```

**Search:**
```
find "keyword"
search for "phrase"
where is "section name"
```

**Update:**
```
change [old] to [new]
update section X
modify paragraph Y
```

**Info:**
```
count paragraphs
show stats
document info
```

---

## 🎯 Testing Checklist

Use these to verify all functionality:

- [ ] Get document outline
- [ ] Search for a term
- [ ] Get specific paragraph
- [ ] Update a paragraph
- [ ] Get breadcrumb info
- [ ] Count sections
- [ ] List subsections
- [ ] Complex multi-step query
- [ ] Error handling (invalid section)
- [ ] Verify update success

---

## 🔗 More Information

- **Full Documentation:** [README.md](README.md)
- **Testing Guide:** [TESTING.md](TESTING.md)
- **Architecture:** See README.md "How It Works"

---

**Happy document editing! 🚀**

For best results, use GPT-4 or Claude Sonnet for the LLM backend.
