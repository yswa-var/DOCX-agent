#!/bin/bash

# DOCX Agent - Stop All Services

echo "🛑 Stopping DOCX Agent - All Services"
echo ""

# Function to kill process on port
kill_port() {
    local port=$1
    local service_name=$2
    
    if netstat -tuln | grep -q ":$port "; then
        echo "🔄 Stopping $service_name on port $port..."
        fuser -k $port/tcp 2>/dev/null || true
        sleep 1
        
        if netstat -tuln | grep -q ":$port "; then
            echo "   ⚠️  Force killing on port $port..."
            sudo fuser -k $port/tcp 2>/dev/null || true
        fi
        echo "   ✅ $service_name stopped"
    else
        echo "   ℹ️  $service_name not running on port $port"
    fi
}

# Kill specific processes
echo "🔄 Stopping processes..."
pkill -f "langgraph dev" 2>/dev/null || true
pkill -f "uvicorn app:app" 2>/dev/null || true
pkill -f "python app.py" 2>/dev/null || true

# Kill by ports
kill_port "8123" "LangGraph Server"
kill_port "8000" "Backend API"
kill_port "3978" "Teams Bot"

echo ""
echo "✅ All services stopped successfully!"
echo ""
echo "🔍 To verify, run: make status"