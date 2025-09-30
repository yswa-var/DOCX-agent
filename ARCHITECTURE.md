# 🏗️ System Architecture Overview

## Complete System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Chat Platforms Layer                          │
│                                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ Telegram │  │ Discord  │  │  Slack   │  │ WhatsApp │  ...   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │
│       │             │             │             │                │
│       └─────────────┴─────────────┴─────────────┘                │
│                          │                                        │
│                          ▼                                        │
│              ┌───────────────────────┐                           │
│              │   Your Bot Client     │                           │
│              │  (Python/Node/etc.)   │                           │
│              └───────────┬───────────┘                           │
└──────────────────────────┼───────────────────────────────────────┘
                           │ HTTP/REST
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Backend API Layer                             │
│                    (FastAPI - Port 8000)                         │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  app.py                                                  │   │
│  │  • POST /api/chat        - Send messages                │   │
│  │  • POST /api/approve     - Handle approvals             │   │
│  │  • GET  /api/sessions    - Manage sessions              │   │
│  │  • GET  /health          - Health check                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌────────────────────┐      ┌───────────────────────┐         │
│  │ session_manager.py │◄─────┤   agent_runner.py     │         │
│  │                    │      │                       │         │
│  │ • User sessions    │      │ • LangGraph client    │         │
│  │ • Thread tracking  │      │ • Interrupt handling  │         │
│  │ • Approval state   │      │ • Message routing     │         │
│  └────────────────────┘      └───────────┬───────────┘         │
│                                           │                      │
└───────────────────────────────────────────┼──────────────────────┘
                                            │ SDK / Local Import
                                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                 LangGraph Agent Layer                            │
│                 (Port 8123 or Local)                             │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  graph.py - Agent Workflow                              │   │
│  │                                                          │   │
│  │  ┌──────────┐     ┌──────────────┐     ┌──────────┐   │   │
│  │  │call_model│────►│approval_node │────►│  tools   │   │   │
│  │  └────┬─────┘     └──────┬───────┘     └────┬─────┘   │   │
│  │       │                  │                   │          │   │
│  │       └──────────────────┴───────────────────┘          │   │
│  │                          │                              │   │
│  │                    interrupt() ◄── Human approval      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌───────────────┐  ┌────────────────┐  ┌─────────────────┐   │
│  │   tools.py    │  │   state.py     │  │  context.py     │   │
│  │               │  │                │  │                 │   │
│  │ • index_docx  │  │ • Messages     │  │ • System prompt │   │
│  │ • apply_edit  │  │ • Pending ops  │  │ • Model config  │   │
│  │ • search      │  │ • Is last step │  │                 │   │
│  │ • get_outline │  └────────────────┘  └─────────────────┘   │
│  └───────┬───────┘                                             │
└──────────┼─────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│              Document Processing Layer                           │
│                                                                   │
│  ┌──────────────────┐       ┌─────────────────────────┐        │
│  │ docx_manager.py  │◄──────┤   docx_indexer.py       │        │
│  │                  │       │                         │        │
│  │ • Read/Write     │       │ • Build index           │        │
│  │ • Anchor system  │       │ • Create anchors        │        │
│  │ • Update paras   │       │ • Extract structure     │        │
│  └────────┬─────────┘       └─────────────────────────┘        │
│           │                                                      │
│           ▼                                                      │
│  ┌───────────────────────────────────────────────┐             │
│  │          master.docx                          │             │
│  │  (Your actual document file)                  │             │
│  └───────────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow: Read Operation (No Approval)

```
User: "Show me the document outline"
  │
  ├─► Backend receives via /api/chat
  │
  ├─► Creates/Gets session for user
  │
  ├─► Sends to LangGraph agent
  │
  ├─► Agent calls get_document_outline tool
  │
  ├─► DOCX Manager reads document structure
  │
  ├─► Returns outline data
  │
  ├─► Agent formats response
  │
  ├─► Backend receives response
  │
  └─► User sees: "Here's the outline: ..."

✅ No approval needed - direct response
```

## Data Flow: Write Operation (With Approval)

```
User: "Update section 2.1 to say 'New Text'"
  │
  ├─► Backend receives via /api/chat
  │
  ├─► Creates/Gets session for user
  │
  ├─► Sends to LangGraph agent
  │
  ├─► Agent recognizes write operation
  │
  ├─► Routes to approval_node
  │
  ├─► interrupt() called with operation details
  │       │
  │       └─► {
  │             "tool_name": "apply_edit",
  │             "args": {...},
  │             "description": "Update operation..."
  │           }
  │
  ├─► Backend receives interrupt data
  │
  ├─► Stores in session.pending_approval
  │
  └─► User sees: "🔔 Approval Required... Reply 'yes' or 'no'"

⏸️ Paused - waiting for approval

User: "yes"
  │
  ├─► Backend receives via /api/approve
  │
  ├─► Retrieves pending approval from session
  │
  ├─► Resumes LangGraph with Command(resume="yes")
  │
  ├─► Agent executes apply_edit tool
  │
  ├─► DOCX Manager updates document
  │
  ├─► Agent confirms completion
  │
  ├─► Backend clears pending_approval
  │
  └─► User sees: "✅ Operation completed successfully"

✅ Approved and executed
```

## Component Responsibilities

### Backend API (`backend/`)

| Component | Responsibility |
|-----------|---------------|
| `app.py` | Main FastAPI server, REST endpoints, request routing |
| `session_manager.py` | User session lifecycle, approval state storage |
| `agent_runner.py` | LangGraph communication (SDK or local) |
| `test_api.py` | Automated testing suite |
| `start.sh` | Startup script with checks |

### LangGraph Agent (`main/src/react_agent/`)

| Component | Responsibility |
|-----------|---------------|
| `graph.py` | Agent workflow, approval routing, interrupts |
| `state.py` | Conversation state management |
| `tools.py` | Document operations (read/write) |
| `context.py` | Configuration and prompts |
| `docx_manager.py` | Document read/write operations |
| `docx_indexer.py` | Document structure indexing |

## Key Features

### 1. Human-in-the-Loop (Approval System)

```python
# In graph.py
async def approval_node(state: State):
    # Pause execution
    approval = interrupt({
        "tool_name": "apply_edit",
        "description": "Approve this edit?"
    })
    
    # Resume based on response
    if approval == "yes":
        return {"proceed": True}
    else:
        return {"proceed": False}
```

```python
# In backend
if result.get("requires_approval"):
    # Store approval data
    session.pending_approval = result["approval_data"]
    
    # Show to user
    return "🔔 Approval Required... yes/no?"

# When user responds
if user_says_yes:
    agent_runner.resume_with_approval(approved=True)
```

### 2. Session Management

```python
Session:
  - session_id: "abc-123"
  - user_id: "telegram_456"
  - thread_id: "xyz-789"  # LangGraph conversation
  - pending_approval: {...} or None
  - created_at: timestamp
  - last_activity: timestamp
```

**Features:**
- Auto-created on first message
- Maintains conversation history via thread_id
- Stores pending approvals
- Auto-cleanup after timeout (60 min default)

### 3. Multi-Platform Support

Same API works for all platforms:

```python
# Telegram
POST /api/chat
{
  "user_id": "telegram_12345",
  "message": "...",
  "platform": "telegram"
}

# Discord
POST /api/chat
{
  "user_id": "discord_67890",
  "message": "...",
  "platform": "discord"
}

# Any platform
POST /api/chat
{
  "user_id": "myapp_user123",
  "message": "...",
  "platform": "myapp"
}
```

## Configuration

### Backend (`.env`)

```bash
LANGGRAPH_URL=http://localhost:8123  # or empty for local
OPENAI_API_KEY=sk-...
HOST=0.0.0.0
PORT=8000
SESSION_TIMEOUT_MINUTES=60
```

### LangGraph (`main/.env`)

```bash
OPENAI_API_KEY=sk-...
DOCX_PATH=/path/to/master.docx
```

## Deployment Architecture

### Option 1: All Local (Development)

```
┌────────────────────────┐
│   Your Computer        │
│                        │
│  ┌─────────────────┐  │
│  │ Backend :8000   │  │
│  └────────┬────────┘  │
│           │           │
│           ▼           │
│  ┌─────────────────┐  │
│  │ LangGraph :8123 │  │
│  └─────────────────┘  │
└────────────────────────┘
```

### Option 2: Remote Backend (Production)

```
┌───────────────────┐
│  Cloud (Railway)  │
│  ┌─────────────┐  │
│  │Backend :8000│  │
│  └──────┬──────┘  │
└─────────┼─────────┘
          │ HTTPS
          ▼
┌───────────────────┐
│  Cloud/Local      │
│  ┌─────────────┐  │
│  │LangGraph    │  │
│  └─────────────┘  │
└───────────────────┘
```

### Option 3: Fully Deployed

```
┌─────────────────┐      ┌──────────────────┐
│  Chat Platform  │─────►│  Cloud Backend   │
└─────────────────┘      │  (Railway)       │
                         │  Port: 8000      │
                         └────────┬─────────┘
                                  │ SDK
                                  ▼
                         ┌──────────────────┐
                         │  LangGraph Cloud │
                         │  or Self-hosted  │
                         └──────────────────┘
```

## Security Considerations

### Current State (Development)

- ✅ Basic input validation
- ✅ Session isolation
- ✅ Approval workflow
- ⚠️ No authentication
- ⚠️ Open CORS
- ⚠️ No rate limiting

### Production Recommendations

```python
# Add in app.py

# 1. API Key Authentication
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403)
    return api_key

# 2. Rate Limiting
from slowapi import Limiter
limiter = Limiter(key_func=lambda: request.client.host)

@app.post("/api/chat")
@limiter.limit("10/minute")
async def chat(request: Request, message: ChatMessage):
    ...

# 3. HTTPS Only
app.add_middleware(HTTPSRedirectMiddleware)

# 4. Restricted CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    ...
)
```

## Monitoring & Observability

### Health Check

```bash
curl http://localhost:8000/health

{
  "status": "healthy",
  "timestamp": "2025-09-30T10:30:00Z",
  "active_sessions": 5
}
```

### Metrics to Track

- Active sessions count
- Approval request rate
- Approval/rejection ratio
- Average response time
- Error rate
- Session timeout rate

### Logging

```python
# Current: Console logging
logger.info(f"User {user_id} sent message")
logger.error(f"Error processing: {error}")

# Production: Structured logging
import structlog
logger.info("message_received", 
            user_id=user_id,
            platform=platform,
            message_length=len(message))
```

## Testing Strategy

### 1. Backend Unit Tests

```bash
cd backend
python test_api.py
```

Tests:
- Health check
- Session creation
- Message processing
- Approval workflow
- Session management

### 2. Integration Tests

```python
# Test complete flow
def test_approval_flow():
    # Send write operation
    response = client.chat("user1", "Update doc")
    assert response["requires_approval"]
    
    # Approve
    result = client.approve("user1", session_id, True)
    assert "success" in result["message"]
```

### 3. LangGraph Tests

```bash
cd main
pytest tests/
```

Tests:
- Graph execution
- Tool functionality
- Approval routing
- State management

## Troubleshooting Guide

| Issue | Solution |
|-------|----------|
| Cannot connect to backend | Check if running: `curl localhost:8000/health` |
| Backend can't reach LangGraph | Verify `LANGGRAPH_URL` in `.env` |
| Approval not working | Check `WRITE_TOOLS` in `graph.py` |
| Session not found | May have timed out (default: 60 min) |
| Import errors | Install: `pip install -r requirements.txt` |
| Port already in use | Change `PORT` in `.env` or kill process |

## Performance Considerations

### Session Storage

- **Current**: In-memory (not persistent)
- **Production**: Use Redis or database

```python
# Future: Redis-backed sessions
from redis import Redis
redis_client = Redis(host='localhost', port=6379)

class RedisSessionManager:
    def get_session(self, session_id):
        data = redis_client.get(f"session:{session_id}")
        return Session(**json.loads(data))
```

### Scaling

**Horizontal Scaling:**
```bash
# Run multiple backend instances
gunicorn app:app --workers 4 --bind 0.0.0.0:8000
```

**Load Balancing:**
```
         ┌─► Backend Instance 1
Load ────┼─► Backend Instance 2
Balancer └─► Backend Instance 3
```

## Next Steps

1. ✅ **Test locally** - Verify everything works
2. ✅ **Integrate platform** - Connect your chat app
3. ✅ **Deploy backend** - Put online
4. ⏭️ **Add authentication** - Secure your API
5. ⏭️ **Add monitoring** - Track usage
6. ⏭️ **Scale** - Handle more users

## Quick Links

- 📖 **Quick Start**: `BACKEND_QUICKSTART.md`
- 📚 **Detailed Docs**: `backend/README.md`
- 📋 **Summary**: `BACKEND_SUMMARY.md`
- 🧪 **Test**: `backend/test_api.py`
- 💡 **Examples**: `backend/examples/`

---

**Architecture designed for:**
- ✅ Simplicity - Easy to understand and modify
- ✅ Flexibility - Works with any platform
- ✅ Reliability - Handles errors gracefully
- ✅ Scalability - Can grow with your needs

**Built with**: FastAPI + LangGraph + Python 🚀
