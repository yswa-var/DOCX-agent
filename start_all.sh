#!/bin/bash

# DOCX Agent - Start All Services
# This script starts all services in the correct order in separate terminals

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "🚀 Starting DOCX Agent - All Services"
echo "📁 Project Root: $PROJECT_ROOT"
echo ""

# Function to check if a service is running on a port
check_port() {
    local port=$1
    local service_name=$2
    local max_wait=$3
    local count=0
    
    echo "⏳ Waiting for $service_name to start on port $port..."
    
    while [ $count -lt $max_wait ]; do
        # Use multiple methods to check port
        if command -v ss >/dev/null 2>&1; then
            # Use ss (modern replacement for netstat)
            if ss -tuln | grep -q ":$port "; then
                echo "✅ $service_name is running on port $port"
                return 0
            fi
        elif command -v lsof >/dev/null 2>&1; then
            # Use lsof as alternative
            if lsof -i :$port >/dev/null 2>&1; then
                echo "✅ $service_name is running on port $port"
                return 0
            fi
        elif command -v netstat >/dev/null 2>&1; then
            # Use netstat if available
            if netstat -tuln | grep -q ":$port "; then
                echo "✅ $service_name is running on port $port"
                return 0
            fi
        else
            # Fallback: try to connect to port
            if timeout 1 bash -c "</dev/tcp/localhost/$port" 2>/dev/null; then
                echo "✅ $service_name is running on port $port"
                return 0
            fi
        fi
        
        sleep 2
        count=$((count + 1))
        echo "   ... waiting ($count/$max_wait)"
    done
    
    echo "❌ $service_name failed to start on port $port within ${max_wait} attempts"
    return 1
}

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

# Function to start service in new terminal
start_service() {
    local service_name=$1
    local working_dir=$2
    local command=$3
    local port=$4
    local wait_time=$5
    
    echo ""
    echo "🔄 Starting $service_name..."
    echo "📂 Directory: $working_dir"
    echo "🏃 Command: $command"
    
    # Different terminal commands based on what's available
    if command -v kitty >/dev/null 2>&1; then
        kitty --detach --directory="$working_dir" --title="DOCX Agent - $service_name" bash -c "$command; read -p 'Press Enter to close...'" &
    elif command -v gnome-terminal >/dev/null 2>&1; then
        gnome-terminal --working-directory="$working_dir" --title="DOCX Agent - $service_name" -- bash -c "$command; read -p 'Press Enter to close...'" &
    elif command -v xterm >/dev/null 2>&1; then
        xterm -T "DOCX Agent - $service_name" -e "cd '$working_dir' && $command; read -p 'Press Enter to close...'" &
    elif command -v konsole >/dev/null 2>&1; then
        konsole --workdir "$working_dir" --title "DOCX Agent - $service_name" -e bash -c "$command; read -p 'Press Enter to close...'" &
    elif command -v terminator >/dev/null 2>&1; then
        terminator --working-directory="$working_dir" --title="DOCX Agent - $service_name" -e "bash -c '$command; read -p \"Press Enter to close...\"'" &
    elif command -v tilix >/dev/null 2>&1; then
        tilix --working-directory="$working_dir" --title="DOCX Agent - $service_name" -e "bash -c '$command; read -p \"Press Enter to close...\"'" &
    else
        echo "❌ No supported terminal emulator found!"
        echo "   Please install one of: kitty, gnome-terminal, xterm, konsole, terminator, or tilix"
        echo "   Or run services manually:"
        echo "   cd $working_dir && $command"
        exit 1
    fi
    
    # Wait for service to start if port is specified
    if [ ! -z "$port" ] && [ ! -z "$wait_time" ]; then
        sleep 3  # Give terminal time to start
        check_port "$port" "$service_name" "$wait_time"
    fi
}

# Kill existing services function
cleanup_services() {
    echo "🧹 Cleaning up existing services..."
    
    # Kill processes on known ports
    for port in 8123 8000 3978; do
        if port_in_use "$port"; then
            echo "   Killing service on port $port..."
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
    echo "✅ Cleanup completed"
}

# Function to install missing tools
install_tools() {
    echo "🔧 Installing missing network tools..."
    
    if command -v apt-get >/dev/null 2>&1; then
        # Ubuntu/Debian
        sudo apt-get update && sudo apt-get install -y net-tools
    elif command -v yum >/dev/null 2>&1; then
        # RHEL/CentOS
        sudo yum install -y net-tools
    elif command -v dnf >/dev/null 2>&1; then
        # Fedora
        sudo dnf install -y net-tools
    elif command -v pacman >/dev/null 2>&1; then
        # Arch Linux
        sudo pacman -S net-tools
    else
        echo "⚠️  Could not install net-tools automatically"
        echo "   Please install manually: sudo apt-get install net-tools"
    fi
}

# Main execution
echo "🔧 Checking dependencies..."

# Check if we have tools to check ports
if ! command -v ss >/dev/null 2>&1 && ! command -v lsof >/dev/null 2>&1 && ! command -v netstat >/dev/null 2>&1; then
    echo "⚠️  No network tools found (ss, lsof, or netstat)"
    read -p "📥 Install net-tools package? (y/N): " install_tools_choice
    if [[ $install_tools_choice =~ ^[Yy]$ ]]; then
        install_tools
    else
        echo "ℹ️  Continuing without port checking..."
    fi
fi

# Check if all directories exist
for dir in "main" "backend" "teams"; do
    if [ ! -d "$PROJECT_ROOT/$dir" ]; then
        echo "❌ Directory $dir not found in project root!"
        exit 1
    fi
done

# Check if Teams test tool exists (updated path)
TEAMS_TEST_TOOL_PATH="$PROJECT_ROOT/devTools/teamsapptester/node_modules/@microsoft/teams-app-test-tool/cli.js"
if [ ! -f "$TEAMS_TEST_TOOL_PATH" ]; then
    echo "⚠️  Teams test tool not found at: $TEAMS_TEST_TOOL_PATH"
    echo "   Make sure you've installed the Teams App Test Tool"
else
    echo "✅ Teams test tool found"
fi

# Check if environment files exist
for env_file in "main/.env" "backend/.env" "teams/.env.teams"; do
    if [ ! -f "$PROJECT_ROOT/$env_file" ]; then
        echo "⚠️  Warning: $env_file not found"
    fi
done

# Option to cleanup existing services
read -p "🧹 Clean up existing services first? (y/N): " cleanup
if [[ $cleanup =~ ^[Yy]$ ]]; then
    cleanup_services
fi

echo ""
echo "🚀 Starting services in order..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. Start LangGraph Server (Main)
start_service \
    "LangGraph Server" \
    "$PROJECT_ROOT/main" \
    "./start_mcp_server.sh" \
    "2024" \
    "30"

# 2. Start Backend Server
start_service \
    "Backend API" \
    "$PROJECT_ROOT/backend" \
    "./start.sh" \
    "8000" \
    "15"

# 3. Start Teams Bot
start_service \
    "Teams Bot" \
    "$PROJECT_ROOT/teams" \
    "python app.py" \
    "3978" \
    "10"

# 4. Start Teams Local Test Tool (updated path and working directory)
if [ -f "$TEAMS_TEST_TOOL_PATH" ]; then
    start_service \
        "Teams Local Test Tool" \
        "$PROJECT_ROOT/teams" \
        "node ../devTools/teamsapptester/node_modules/@microsoft/teams-app-test-tool/cli.js start" \
        "" \
        ""
else
    echo ""
    echo "⚠️  Teams Local Test Tool not found!"
    echo "   To install it, run in the project root:"
    echo "   mkdir -p devTools/teamsapptester"
    echo "   npm i @microsoft/teams-app-test-tool --prefix 'devTools/teamsapptester'"
    echo "   or follow the Teams App Test Tool setup guide"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 All services started successfully!"
echo ""
echo "📊 Service Status:"
echo "   🌐 LangGraph Server:     http://localhost:8123"
echo "   🔧 Backend API:          http://localhost:8000"
echo "   🤖 Teams Bot:            http://localhost:3978"
echo "   🧪 Teams Test Tool:      http://localhost:3978 (if installed)"
echo "   📖 API Docs:             http://localhost:8000/docs"
echo ""
echo "🔍 To monitor services:"
echo "   curl http://localhost:8123/health    # LangGraph"
echo "   curl http://localhost:8000/health    # Backend"
echo ""
echo "💡 Teams Test Tool Usage:"
echo "   - The test tool provides a local Teams-like interface"
echo "   - Test your bot without needing actual Teams"
echo "   - Access via web browser on the port shown"
echo ""
echo "⚠️  Note: Each service is running in its own terminal window."
echo "   Close terminal windows to stop individual services."
echo ""
echo "🛑 To stop all services:"
echo "   ./stop_all.sh (if available) or close all terminal windows"
echo ""
echo "✅ Setup complete! Your DOCX Agent is ready for use."