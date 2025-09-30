# 🎉 CSV Storage Added!

## What Changed?

Your backend now saves sessions to a **CSV file** instead of only in memory!

## Benefits

✅ **Sessions survive server restarts**  
✅ **No database needed**  
✅ **Easy to inspect**: Just open `sessions.csv`  
✅ **Free deployment friendly**: Works everywhere  

## Quick Start

### 1. Just Run It!

```bash
cd backend
./start.sh
```

The CSV file (`sessions.csv`) is automatically created in the `backend/` directory.

### 2. See Your Sessions

```bash
# View the CSV file
cd backend
cat sessions.csv
```

Example:
```csv
session_id,user_id,platform,thread_id,created_at,last_activity,pending_approval,metadata
abc-123,telegram_456,telegram,xyz-789,2025-09-30T10:30:00,2025-09-30T11:45:00,"",{}
def-456,discord_789,discord,uvw-012,2025-09-30T09:15:00,2025-09-30T11:30:00,"",{}
```

### 3. Configuration (Optional)

Want to store the CSV somewhere else? Set in `.env`:

```bash
# Custom CSV path
SESSIONS_CSV_PATH=/path/to/my/sessions.csv
```

## What Gets Saved?

Every session contains:
- **session_id**: Unique session ID
- **user_id**: User identifier (e.g., `telegram_12345`)
- **platform**: Platform name (`telegram`, `discord`, `api`, etc.)
- **thread_id**: LangGraph conversation thread
- **created_at**: When session was created
- **last_activity**: Last activity timestamp
- **pending_approval**: Any pending approval data (JSON)
- **metadata**: Custom metadata (JSON)

## Features

### Auto-Save

Every change is automatically saved:

```python
# User sends message → Session updated → CSV saved
# Approval requested → Approval data stored → CSV saved
# Session deleted → Removed from CSV → CSV saved
```

### Auto-Load

When backend starts, it loads all active sessions:

```
🚀 Starting backend...
📂 Loading sessions from sessions.csv...
✅ Loaded 5 sessions from sessions.csv
🌐 Server ready!
```

### Auto-Cleanup

Expired sessions (60 min of inactivity) are:
- Automatically cleaned up every 5 minutes
- Not loaded on server restart

## Backup & Restore

### Backup

```bash
cd backend
cp sessions.csv sessions_backup_$(date +%Y%m%d).csv
```

### Restore

```bash
cd backend
cp sessions_backup_20250930.csv sessions.csv
# Restart server
./start.sh
```

## Monitoring

### Count Active Sessions

```bash
wc -l backend/sessions.csv
```

### View All Sessions

```bash
cd backend
column -t -s, sessions.csv
```

### Find User's Sessions

```bash
grep "telegram_12345" backend/sessions.csv
```

## Security

The CSV file is automatically added to `.gitignore` to prevent committing user data.

```bash
# backend/.gitignore
sessions.csv
sessions_*.csv
*.csv
```

## Testing

Test the CSV storage:

```bash
cd backend

# 1. Start server
python app.py

# 2. In another terminal, send a test message
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_123", "message": "Hello"}'

# 3. Check the CSV was created
cat sessions.csv
```

You should see your test session in the CSV!

## File Location

```
backend/
├── app.py
├── session_manager.py
├── sessions.csv          ← Created here automatically
├── .gitignore            ← CSV files excluded
└── ...
```

## When to Use Database?

CSV is perfect for:
- ✅ Personal projects
- ✅ Small to medium bots (< 1000 concurrent users)
- ✅ Free deployments (Railway, Render, Fly.io)
- ✅ Development and testing

Consider upgrading to database (Redis/PostgreSQL) if:
- ❌ More than 10,000 active sessions
- ❌ High write frequency (>100/sec)
- ❌ Need distributed storage
- ❌ Need complex queries

## Troubleshooting

### CSV Not Created?

Check write permissions:
```bash
cd backend
touch sessions.csv
chmod 644 sessions.csv
```

### Sessions Not Loading?

Check the server logs when it starts:
```bash
./start.sh
# Look for: "Loaded X sessions from sessions.csv"
```

### Want to Start Fresh?

```bash
cd backend
rm sessions.csv
./start.sh
```

A new empty CSV will be created.

## Complete Documentation

For detailed information, see:
- **Full docs**: `backend/CSV_STORAGE.md`
- **Backend docs**: `backend/README.md`
- **Quick start**: `BACKEND_QUICKSTART.md`

## Summary

Your backend now has **persistent session storage** with zero configuration:

✅ Automatic CSV creation  
✅ Auto-save on every change  
✅ Auto-load on startup  
✅ No database required  
✅ Easy backup/restore  
✅ Human-readable format  

**Just start the server and it works!** 🚀

---

**Next Steps**:
1. Test it: `cd backend && python app.py`
2. Check CSV: `cat backend/sessions.csv`
3. Integrate your bot and see sessions persist!
