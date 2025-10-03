#!/bin/bash

# DOCX Agent - Stop All Services
# This script stops all running services gracefully

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "🛑 Stopping DOCX Agent - All Services"
echo "📁 Project Root: $PROJECT_ROOT"
echo ""

# Function to check if port is in use
port_in_use() {
    local port=$1
    
    if command -v ss >/dev/null 2>&1; then
        ss -tuln | grep -q ":$port "
    elif command -v lsof >/dev/null 2>&1; then
        lsof -i :$port >/dev/null 2>&1
    elif command -v netstat >/dev/null 2>&1; then
        netstat -tuln | grep -q ":$port "
    else
        timeout 1 bash -c "</dev/tcp/localhost/$port" 2>/dev/null
    fi
}

# Function to stop services
stop_services() {
    echo "🧹 Stopping all services..."
    
    # Kill processes from PID files first
    if [ -d "$PROJECT_ROOT/logs" ]; then
        for pid_file in "$PROJECT_ROOT/logs"/*.pid; do
            if [ -f "$pid_file" ]; then
                local pid=$(cat "$pid_file")
                local service_name=$(basename "$pid_file" .pid)
                if kill -0 "$pid" 2>/dev/null; then
                    echo "   Stopping $service_name (PID: $pid)..."
                    kill "$pid" 2>/dev/null || true
                    sleep 1
                    if kill -0 "$pid" 2>/dev/null; then
                        echo "   Force stopping $service_name..."
                        kill -9 "$pid" 2>/dev/null || true
                    fi
                fi
                rm -f "$pid_file"
            fi
        done
    fi
    
    # Kill processes on known ports
    for port in 2024 8000 3978; do
        if port_in_use "$port"; then
            echo "   Stopping service on port $port..."
            # Try different methods to kill
            if command -v fuser >/dev/null 2>&1; then
                fuser -k $port/tcp 2>/dev/null || true
            elif command -v lsof >/dev/null 2>&1; then
                lsof -ti :$port | xargs kill -9 2>/dev/null || true
            fi
        fi
    done
    
    # Kill specific processes
    pkill -f "langgraph dev" 2>/dev/null || true
    pkill -f "uvicorn app:app" 2>/dev/null || true
    pkill -f "python app.py" 2>/dev/null || true
    pkill -f "teams-app-test-tool" 2>/dev/null || true
    pkill -f "@microsoft/teams-app-test-tool" 2>/dev/null || true
    
    sleep 2
    echo "✅ All services stopped"
}

# Check if any services are running
services_running=false
for port in 2024 8000 3978; do
    if port_in_use "$port"; then
        services_running=true
        break
    fi
done

if [ "$services_running" = false ] && [ ! -d "$PROJECT_ROOT/logs" ]; then
    echo "ℹ️  No services appear to be running"
    exit 0
fi

# Confirm before stopping
read -p "⚠️  Are you sure you want to stop all DOCX Agent services? (y/N): " confirm
if [[ ! $confirm =~ ^[Yy]$ ]]; then
    echo "❌ Operation cancelled"
    exit 0
fi

stop_services

echo ""
echo "🔍 Checking if services are stopped..."
sleep 1

# Verify services are stopped
all_stopped=true
for port in 2024 8000 3978; do
    if port_in_use "$port"; then
        echo "⚠️  Service still running on port $port"
        all_stopped=false
    fi
done

if [ "$all_stopped" = true ]; then
    echo "✅ All services successfully stopped"
else
    echo "⚠️  Some services may still be running"
    echo "   You may need to stop them manually"
fi

echo ""
echo "📝 Log files preserved in: $PROJECT_ROOT/logs/"
echo "   You can review them or delete if no longer needed"