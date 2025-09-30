# 🔐 Human-in-the-Loop Approval System

This document explains how the human approval system works for critical document operations.

## 📋 Overview

The DOCX Agent now requires **human approval** for all write operations (update/edit/delete) before they are executed. This prevents accidental modifications and gives you control over document changes.

## 🎯 What Gets Approved?

### Operations Requiring Approval ✋
- ✅ **`update_paragraph()`** - Modifying document text
- ✅ (Future) **`delete_paragraph()`** - Removing content
- ✅ (Future) **`insert_paragraph()`** - Adding new content

### Operations NOT Requiring Approval 👁️
- ❌ **`get_paragraph()`** - Reading content (read-only)
- ❌ **`get_document_outline()`** - Viewing structure (read-only)
- ❌ **`search_document()`** - Searching text (read-only)
- ❌ **`search()`** - Web search (external, read-only)

## 🔄 How It Works

### Flow Diagram

```
User: "Update section 2.1 to say 'Company Profile'"
        ↓
   LLM decides to call update_paragraph()
        ↓
   🛑 APPROVAL NODE (INTERRUPT)
        ↓
   Shows operation details & waits for approval
        ↓
   ┌─────────────────┬─────────────────┐
   │   APPROVED ✅    │   REJECTED ❌    │
   ├─────────────────┼─────────────────┤
   │ Execute tool    │ Cancel operation │
   │ Update document │ Notify user      │
   └─────────────────┴─────────────────┘
        ↓
   Return result to user
```

## 💻 Usage

### Using LangGraph Studio

1. **Start the server:**
   ```bash
   cd /Users/yash/Documents/rfp/DOCX-agent/main
   export OPENAI_API_KEY="sk-your-key"
   langgraph dev
   ```

2. **Open Studio:** http://localhost:8000

3. **Send an update request:**
   ```
   "Update section 2.1 to say 'Company Profile'"
   ```

4. **Review the approval prompt:**
   ```
   **Update Operation**
   - Location: ["body", 0, 0, 0, 95]
   - New text: Company Profile
   
   Do you approve this change? (yes/no)
   ```

5. **Respond with approval:**
   - Type: `yes`, `y`, `approve`, `approved`, or `true` to approve
   - Type: `no`, `n`, `reject`, `rejected`, or `false` to reject

6. **See the result:**
   - ✅ Approved: Document is updated, success message shown
   - ❌ Rejected: No changes made, cancellation message shown

### Using Python SDK

```python
from langgraph_sdk import get_client
from langgraph_sdk.schema import Command

client = get_client(url="http://localhost:8000")
assistant_id = "agent"

# Create a thread
thread = await client.threads.create()
thread_id = thread["thread_id"]

# Run until interrupt
result = await client.runs.wait(
    thread_id,
    assistant_id,
    input={"messages": [{"role": "user", "content": "Update section 2.1 to say 'Company Profile'"}]}
)

# Check the interrupt details
print(result['__interrupt__'])
# Shows:
# [
#   {
#     'value': {
#       'type': 'approval_request',
#       'tool_name': 'update_paragraph',
#       'args': {...},
#       'description': '...'
#     },
#     'resumable': True,
#     ...
#   }
# ]

# Approve the operation
result = await client.runs.wait(
    thread_id,
    assistant_id,
    command=Command(resume="yes")
)

print(result)  # Document updated!
```

## 🔧 Configuration

### Add More Tools to Approval List

Edit `main/src/react_agent/graph.py`:

```python
# Line ~92
WRITE_TOOLS = {
    "update_paragraph",
    "delete_paragraph",    # Add this
    "insert_paragraph",    # Add this
}
```

### Customize Approval Messages

Edit the `approval_node` function in `graph.py`:

```python
# Around line 135
if tool_name == "update_paragraph":
    description = (
        f"**Update Operation**\n"
        f"- Location: {anchor}\n"
        f"- New text: {new_text[:100]}...\n\n"
        f"Do you approve this change? (yes/no)"
    )
elif tool_name == "your_custom_tool":
    description = "Your custom approval message"
```

### Disable Approval (Not Recommended)

If you need to disable approval temporarily:

```python
# In graph.py, modify WRITE_TOOLS to be empty
WRITE_TOOLS = {}  # No tools require approval
```

## 📊 Approval Request Format

When an operation needs approval, you'll see:

```json
{
  "type": "approval_request",
  "tool_name": "update_paragraph",
  "tool_call_id": "call_abc123",
  "args": {
    "anchor": ["body", 0, 0, 0, 95],
    "new_text": "Company Profile"
  },
  "description": "**Update Operation**\n- Location: ['body', 0, 0, 0, 95]\n- New text: Company Profile\n\nDo you approve this change? (yes/no)"
}
```

## 🧪 Testing

### Test Script

```bash
# Run the test script
cd /Users/yash/Documents/rfp/DOCX-agent
python test_approval.py
```

This will:
1. ✅ Test approval (approve an update)
2. ❌ Test rejection (reject an update)
3. 👁️ Test read operations (no approval needed)

### Manual Testing in Studio

**Test 1: Approve an Update**
```
User: Update the title to "New Title"
Agent: [Shows approval request]
User: yes
Agent: ✅ Successfully updated!
```

**Test 2: Reject an Update**
```
User: Change section 2 to "Test"
Agent: [Shows approval request]
User: no
Agent: ❌ Operation cancelled by user
```

**Test 3: Read Operations (No Approval)**
```
User: Show me the document outline
Agent: [Immediately shows outline - no approval needed]
```

## 🎯 Use Cases

### 1. **Prevent Accidental Changes**
```
User: "Update all sections to say 'TODO'"
Agent: [Requests approval before mass update]
You: Reject → Document stays safe!
```

### 2. **Review Before Committing**
```
User: "Change the pricing to $50,000"
Agent: [Shows exactly what will change]
You: Review → Approve only if correct
```

### 3. **Multi-User Safety**
```
Junior team member: "Delete section 3"
Agent: [Requests approval]
Senior reviewer: Reviews → Approves/Rejects
```

### 4. **Audit Trail**
All approvals/rejections are logged in the conversation thread, creating an audit trail of who approved what changes.

## 🔍 Troubleshooting

### Problem: Approval not triggered

**Cause:** Tool not in `WRITE_TOOLS` list
**Solution:** Add tool to `WRITE_TOOLS` in `graph.py`

### Problem: Can't resume after approval

**Cause:** No checkpointer configured
**Solution:** Ensure graph is compiled with checkpointer:

```python
from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)
```

### Problem: Approval message not clear

**Cause:** Need better description
**Solution:** Customize approval message in `approval_node()`

## 📚 References

- [LangGraph Human-in-the-Loop Platform Docs](https://docs.langchain.com/langgraph-platform/add-human-in-the-loop)
- [LangGraph Human-in-the-Loop OSS Docs](https://docs.langchain.com/oss/python/langgraph/add-human-in-the-loop)
- [LangGraph interrupt() API](https://docs.langchain.com/oss/python/langgraph/add-human-in-the-loop#pause-using-interrupt)

## 🚀 Next Steps

1. **Test the feature** in LangGraph Studio
2. **Customize approval messages** for your use case
3. **Add more write operations** to the approval list
4. **Implement role-based approvals** (future enhancement)
5. **Add approval history tracking** (future enhancement)

---

**Built with ❤️ using LangGraph's interrupt() function**
