# 🚀 Backend Quick Start Guide

## What Is This?

You asked about using your LangGraph agent as a bot across different platforms. The **confusion about human-in-the-loop** is now **solved**!

### The Problem You Had

LangGraph docs show using `interrupt()` like this:

```python
# In LangGraph Studio
value = interrupt({"description": "Approve?"})
# Then use SDK to resume
client.runs.wait(thread_id, command=Command(resume="yes"))
```

**This doesn't work naturally in chat apps!** 😫

### The Solution: This Backend

This backend translates between:
- ✅ LangGraph's interrupt-based approvals
- ✅ Natural chat conversations

Now your users can just type "yes" or "no" in Telegram, Discord, Slack, or any platform!

## 🎯 How It Works

```
User on Telegram: "Update section 2.1"
         ↓
Backend API (converts to LangGraph format)
         ↓
LangGraph Agent (your existing agent)
         ↓
Backend API (handles interrupt, stores approval state)
         ↓
User sees: "🔔 Approval Required... Reply with 'yes' or 'no'"
         ↓
User: "yes"
         ↓
Backend API (resumes LangGraph with approval)
         ↓
User sees: "✅ Done!"
```

## 📦 What You Get

```
backend/
├── app.py                    # Main FastAPI server
├── session_manager.py        # Handles user sessions
├── agent_runner.py          # Connects to your LangGraph agent
├── requirements.txt         # Python dependencies
├── .env.example            # Configuration template
├── start.sh                # Easy startup script
├── test_api.py             # Test your backend
├── README.md               # Detailed documentation
└── examples/
    └── simple_integration.py  # Integration examples
```

## 🚀 Quick Start (5 Minutes)

### Step 1: Setup Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Create config file
cp .env.example .env

# Edit .env and add your OpenAI key
nano .env
```

### Step 2: Start LangGraph Server

In a **separate terminal**:

```bash
cd main
export OPENAI_API_KEY="your-key-here"
langgraph dev
```

You should see: `Running at http://localhost:8123`

### Step 3: Start Backend

Back in the backend directory:

```bash
./start.sh
```

Or:

```bash
python app.py
```

You should see: `Backend running on http://localhost:8000`

### Step 4: Test It!

```bash
python test_api.py
```

This will run a complete test suite and show you if everything works.

Or visit: **http://localhost:8000/docs** for interactive API playground

## 🧪 Try It Out

### Example 1: Simple Test

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_123",
    "message": "Show me the document outline",
    "platform": "api"
  }'
```

### Example 2: Python Script

```python
import requests

# Send a message
response = requests.post("http://localhost:8000/api/chat", json={
    "user_id": "my_user_123",
    "message": "Search for 'budget' in the document",
    "platform": "my_app"
})

result = response.json()
print(result["message"])

# If approval needed
if result["requires_approval"]:
    print("⚠️ Waiting for approval...")
    
    # Send approval
    approval = requests.post("http://localhost:8000/api/approve", json={
        "user_id": "my_user_123",
        "session_id": result["session_id"],
        "approved": True
    })
    
    print(approval.json()["message"])
```

Run the examples:

```bash
cd examples
python simple_integration.py
```

## 🔌 Integration Guide

### For Any Platform

The backend provides a **simple REST API** that works with any platform:

1. **POST `/api/chat`** - Send user messages
2. **POST `/api/approve`** - Handle approvals
3. **GET `/api/sessions/{user_id}`** - Check session status

### Example: Telegram Bot

```python
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler
import requests

BACKEND_URL = "http://localhost:8000"

async def handle_message(update: Update, context):
    user_id = f"telegram_{update.effective_user.id}"
    message = update.message.text
    
    # Send to backend
    response = requests.post(f"{BACKEND_URL}/api/chat", json={
        "user_id": user_id,
        "message": message,
        "platform": "telegram"
    })
    
    result = response.json()
    
    if result["requires_approval"]:
        # Add approval buttons
        keyboard = [
            [
                InlineKeyboardButton("✅ Approve", callback_data="approve"),
                InlineKeyboardButton("❌ Reject", callback_data="reject")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            result["message"], 
            reply_markup=reply_markup
        )
        
        # Store session_id in context for callback
        context.user_data['session_id'] = result["session_id"]
    else:
        await update.message.reply_text(result["message"])

async def handle_button(update: Update, context):
    query = update.callback_query
    user_id = f"telegram_{query.from_user.id}"
    session_id = context.user_data.get('session_id')
    
    # Send approval
    approved = query.data == "approve"
    response = requests.post(f"{BACKEND_URL}/api/approve", json={
        "user_id": user_id,
        "session_id": session_id,
        "approved": approved
    })
    
    result = response.json()
    
    # Edit message to show result
    await query.edit_message_text(result["message"])

# Setup bot
app = Application.builder().token("YOUR_BOT_TOKEN").build()
app.add_handler(MessageHandler(filters.TEXT, handle_message))
app.add_handler(CallbackQueryHandler(handle_button))
app.run_polling()
```

### Example: Discord Bot

```python
import discord
import requests

BACKEND_URL = "http://localhost:8000"

class ApprovalView(discord.ui.View):
    def __init__(self, user_id, session_id):
        super().__init__()
        self.user_id = user_id
        self.session_id = session_id
    
    @discord.ui.button(label="✅ Approve", style=discord.ButtonStyle.success)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        response = requests.post(f"{BACKEND_URL}/api/approve", json={
            "user_id": self.user_id,
            "session_id": self.session_id,
            "approved": True
        })
        result = response.json()
        await interaction.response.edit_message(content=result["message"], view=None)
    
    @discord.ui.button(label="❌ Reject", style=discord.ButtonStyle.danger)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        response = requests.post(f"{BACKEND_URL}/api/approve", json={
            "user_id": self.user_id,
            "session_id": self.session_id,
            "approved": False
        })
        result = response.json()
        await interaction.response.edit_message(content=result["message"], view=None)

client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    user_id = f"discord_{message.author.id}"
    
    response = requests.post(f"{BACKEND_URL}/api/chat", json={
        "user_id": user_id,
        "message": message.content,
        "platform": "discord"
    })
    
    result = response.json()
    
    if result["requires_approval"]:
        view = ApprovalView(user_id, result["session_id"])
        await message.channel.send(result["message"], view=view)
    else:
        await message.channel.send(result["message"])

client.run("YOUR_BOT_TOKEN")
```

## 🎛️ Configuration

Edit `backend/.env`:

```bash
# Required: LangGraph server URL
LANGGRAPH_URL=http://localhost:8123

# Required: OpenAI API key
OPENAI_API_KEY=sk-your-key-here

# Optional: Server settings
HOST=0.0.0.0
PORT=8000
DEBUG=true
SESSION_TIMEOUT_MINUTES=60
```

## 🔍 Monitoring

### Check Health

```bash
curl http://localhost:8000/health
```

### View Active Sessions

```bash
curl http://localhost:8000/api/sessions
```

### API Documentation

Visit: http://localhost:8000/docs

## ❓ FAQ

### Q: Do I need to modify my LangGraph agent?

**A:** No! Your existing agent works as-is. The backend handles all the translation.

### Q: Can I use this without running LangGraph server?

**A:** Yes! Set `LANGGRAPH_URL=` (empty) in `.env` and the backend will use local graph execution.

### Q: How does approval work in chat apps?

**A:** 
1. User sends: "Update document"
2. Backend detects it needs approval
3. User sees: "Approval required? (yes/no)"
4. User responds: "yes"
5. Backend resumes the agent
6. User sees: "Done!"

No special SDK needed! Just normal messages.

### Q: What operations require approval?

**A:** Currently: `apply_edit` (document updates)

Configure in `main/src/react_agent/graph.py`:

```python
WRITE_TOOLS = {"apply_edit"}  # Add more here
```

### Q: Can I deploy this for free?

**A:** Yes! Options:
- **Local**: Run on your computer (free)
- **Railway**: Free tier available
- **Render**: Free tier available
- **Fly.io**: Free tier available
- **Heroku**: Free tier available (limited)

## 🚀 Next Steps

1. ✅ **Test locally** - Make sure it works
2. ✅ **Integrate with your platform** - Use examples above
3. ✅ **Deploy** - Put it online (see README.md)
4. ✅ **Customize** - Add your own features

## 📚 More Resources

- **Detailed docs**: `backend/README.md`
- **API playground**: http://localhost:8000/docs
- **Examples**: `backend/examples/simple_integration.py`
- **LangGraph docs**: https://docs.langchain.com/langgraph-platform/

## 💡 Key Takeaway

**You don't need to understand LangGraph's `interrupt()` deeply!**

This backend handles all that complexity. Just use simple REST API calls:

```python
# Send message
response = POST /api/chat

# If approval needed
if response["requires_approval"]:
    # Handle approval
    POST /api/approve
```

That's it! 🎉

---

**Questions?** Check `backend/README.md` or run `python test_api.py` to verify everything works!
