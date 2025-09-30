.PHONY: all start stop clean status help test-services install-deps start-test-tool

# Default target
all: help

# Project paths
PROJECT_ROOT := $(shell pwd)
MAIN_DIR := $(PROJECT_ROOT)/main
BACKEND_DIR := $(PROJECT_ROOT)/backend
TEAMS_DIR := $(PROJECT_ROOT)/teams

# Service ports
LANGGRAPH_PORT := 8123
BACKEND_PORT := 8000
TEAMS_PORT := 3978

# Teams test tool path
TEAMS_TEST_TOOL := $(TEAMS_DIR)/devTools/teamsapptester/node_modules/@microsoft/teams-app-test-tool/cli.js

####################
# MAIN COMMANDS
####################

start: ## Start all services in separate terminals
	@echo "🚀 Starting DOCX Agent - All Services"
	@echo "📁 Project Root: $(PROJECT_ROOT)"
	@echo ""
	@$(MAKE) check-deps
	@$(MAKE) cleanup-ports
	@$(MAKE) start-langgraph
	@$(MAKE) wait-for-langgraph
	@$(MAKE) start-backend
	@$(MAKE) wait-for-backend
	@$(MAKE) start-teams
	@$(MAKE) wait-for-teams
	@$(MAKE) start-test-tool
	@echo ""
	@echo "🎉 All services started successfully!"
	@$(MAKE) status

start-langgraph: ## Start LangGraph server
	@echo "🔄 Starting LangGraph Server..."
	@if command -v kitty >/dev/null 2>&1; then \
	    kitty --detach --directory="$(MAIN_DIR)" --title="DOCX Agent - LangGraph" bash -c "./start_mcp_server.sh; read -p 'Press Enter to close...'" & \
	elif command -v gnome-terminal >/dev/null 2>&1; then \
	    gnome-terminal --working-directory="$(MAIN_DIR)" --title="DOCX Agent - LangGraph" -- bash -c "./start_mcp_server.sh; read -p 'Press Enter to close...'" & \
	elif command -v xterm >/dev/null 2>&1; then \
	    xterm -T "DOCX Agent - LangGraph" -e "cd '$(MAIN_DIR)' && ./start_mcp_server.sh; read -p 'Press Enter to close...'" & \
	elif command -v konsole >/dev/null 2>&1; then \
	    konsole --workdir "$(MAIN_DIR)" --title "DOCX Agent - LangGraph" -e bash -c "./start_mcp_server.sh; read -p 'Press Enter to close...'" & \
	elif command -v alacritty >/dev/null 2>&1; then \
	    alacritty --working-directory "$(MAIN_DIR)" --title "DOCX Agent - LangGraph" -e bash -c "./start_mcp_server.sh; read -p 'Press Enter to close...'" & \
	elif command -v terminator >/dev/null 2>&1; then \
	    terminator --working-directory="$(MAIN_DIR)" --title="DOCX Agent - LangGraph" -e "bash -c './start_mcp_server.sh; read -p \"Press Enter to close...\"'" & \
	elif command -v tilix >/dev/null 2>&1; then \
	    tilix --working-directory="$(MAIN_DIR)" --title="DOCX Agent - LangGraph" -e "bash -c './start_mcp_server.sh; read -p \"Press Enter to close...\"'" & \
	else \
	    echo "❌ No supported terminal found!"; \
	    echo "   Supported terminals: kitty, gnome-terminal, xterm, konsole, alacritty, terminator, tilix"; \
	    echo "   For Mac users: Install iTerm2 and use tmux/screen, or run services manually."; \
	    echo "   Manual start: cd $(MAIN_DIR) && ./start_mcp_server.sh"; \
	    exit 1; \
	fi

start-backend: ## Start Backend API server
	@echo "🔄 Starting Backend API..."
	@if command -v kitty >/dev/null 2>&1; then \
	    kitty --detach --directory="$(BACKEND_DIR)" --title="DOCX Agent - Backend" bash -c "./start.sh; read -p 'Press Enter to close...'" & \
	elif command -v gnome-terminal >/dev/null 2>&1; then \
	    gnome-terminal --working-directory="$(BACKEND_DIR)" --title="DOCX Agent - Backend" -- bash -c "./start.sh; read -p 'Press Enter to close...'" & \
	elif command -v xterm >/dev/null 2>&1; then \
	    xterm -T "DOCX Agent - Backend" -e "cd '$(BACKEND_DIR)' && ./start.sh; read -p 'Press Enter to close...'" & \
	elif command -v konsole >/dev/null 2>&1; then \
	    konsole --workdir "$(BACKEND_DIR)" --title "DOCX Agent - Backend" -e bash -c "./start.sh; read -p 'Press Enter to close...'" & \
	elif command -v alacritty >/dev/null 2>&1; then \
	    alacritty --working-directory "$(BACKEND_DIR)" --title "DOCX Agent - Backend" -e bash -c "./start.sh; read -p 'Press Enter to close...'" & \
	elif command -v terminator >/dev/null 2>&1; then \
	    terminator --working-directory="$(BACKEND_DIR)" --title="DOCX Agent - Backend" -e "bash -c './start.sh; read -p \"Press Enter to close...\"'" & \
	elif command -v tilix >/dev/null 2>&1; then \
	    tilix --working-directory="$(BACKEND_DIR)" --title="DOCX Agent - Backend" -e "bash -c './start.sh; read -p \"Press Enter to close...\"'" & \
	else \
	    echo "❌ No supported terminal found!"; \
	    echo "   Supported terminals: kitty, gnome-terminal, xterm, konsole, alacritty, terminator, tilix"; \
	    echo "   For Mac users: Install iTerm2 and use tmux/screen, or run services manually."; \
	    echo "   Manual start: cd $(BACKEND_DIR) && ./start.sh"; \
	    exit 1; \
	fi

start-teams: ## Start Teams bot
	@echo "🔄 Starting Teams Bot..."
	@if command -v kitty >/dev/null 2>&1; then \
	    kitty --detach --directory="$(TEAMS_DIR)" --title="DOCX Agent - Teams Bot" bash -c "python app.py; read -p 'Press Enter to close...'" & \
	elif command -v gnome-terminal >/dev/null 2>&1; then \
	    gnome-terminal --working-directory="$(TEAMS_DIR)" --title="DOCX Agent - Teams Bot" -- bash -c "python app.py; read -p 'Press Enter to close...'" & \
	elif command -v xterm >/dev/null 2>&1; then \
	    xterm -T "DOCX Agent - Teams Bot" -e "cd '$(TEAMS_DIR)' && python app.py; read -p 'Press Enter to close...'" & \
	elif command -v konsole >/dev/null 2>&1; then \
	    konsole --workdir "$(TEAMS_DIR)" --title "DOCX Agent - Teams Bot" -e bash -c "python app.py; read -p 'Press Enter to close...'" & \
	elif command -v alacritty >/dev/null 2>&1; then \
	    alacritty --working-directory "$(TEAMS_DIR)" --title "DOCX Agent - Teams Bot" -e bash -c "python app.py; read -p 'Press Enter to close...'" & \
	elif command -v terminator >/dev/null 2>&1; then \
	    terminator --working-directory="$(TEAMS_DIR)" --title="DOCX Agent - Teams Bot" -e "bash -c 'python app.py; read -p \"Press Enter to close...\"'" & \
	elif command -v tilix >/dev/null 2>&1; then \
	    tilix --working-directory="$(TEAMS_DIR)" --title="DOCX Agent - Teams Bot" -e "bash -c 'python app.py; read -p \"Press Enter to close...\"'" & \
	else \
	    echo "❌ No supported terminal found!"; \
	    echo "   Supported terminals: kitty, gnome-terminal, xterm, konsole, alacritty, terminator, tilix"; \
	    echo "   For Mac users: Install iTerm2 and use tmux/screen, or run services manually."; \
	    echo "   Manual start: cd $(TEAMS_DIR) && python app.py"; \
	    exit 1; \
	fi

start-test-tool: ## Start Teams local test tool
	@echo "🔄 Starting Teams Test Tool..."
	@if [ -f "$(TEAMS_TEST_TOOL)" ]; then \
	    if command -v kitty >/dev/null 2>&1; then \
	        kitty --detach --directory="$(TEAMS_DIR)" --title="DOCX Agent - Teams Test Tool" bash -c "node devTools/teamsapptester/node_modules/@microsoft/teams-app-test-tool/cli.js start; read -p 'Press Enter to close...'" & \
	    elif command -v gnome-terminal >/dev/null 2>&1; then \
	        gnome-terminal --working-directory="$(TEAMS_DIR)" --title="DOCX Agent - Teams Test Tool" -- bash -c "node devTools/teamsapptester/node_modules/@microsoft/teams-app-test-tool/cli.js start; read -p 'Press Enter to close...'" & \
	    elif command -v xterm >/dev/null 2>&1; then \
	        xterm -T "DOCX Agent - Teams Test Tool" -e "cd '$(TEAMS_DIR)' && node devTools/teamsapptester/node_modules/@microsoft/teams-app-test-tool/cli.js start; read -p 'Press Enter to close...'" & \
	    elif command -v konsole >/dev/null 2>&1; then \
	        konsole --workdir "$(TEAMS_DIR)" --title "DOCX Agent - Teams Test Tool" -e bash -c "node devTools/teamsapptester/node_modules/@microsoft/teams-app-test-tool/cli.js start; read -p 'Press Enter to close...'" & \
	    elif command -v alacritty >/dev/null 2>&1; then \
	        alacritty --working-directory "$(TEAMS_DIR)" --title "DOCX Agent - Teams Test Tool" -e bash -c "node devTools/teamsapptester/node_modules/@microsoft/teams-app-test-tool/cli.js start; read -p 'Press Enter to close...'" & \
	    elif command -v terminator >/dev/null 2>&1; then \
	        terminator --working-directory="$(TEAMS_DIR)" --title="DOCX Agent - Teams Test Tool" -e "bash -c 'node devTools/teamsapptester/node_modules/@microsoft/teams-app-test-tool/cli.js start; read -p \"Press Enter to close...\"'" & \
	    elif command -v tilix >/dev/null 2>&1; then \
	        tilix --working-directory="$(TEAMS_DIR)" --title="DOCX Agent - Teams Test Tool" -e "bash -c 'node devTools/teamsapptester/node_modules/@microsoft/teams-app-test-tool/cli.js start; read -p \"Press Enter to close...\"'" & \
	    fi; \
	    echo "✅ Teams Test Tool started"; \
	else \
	    echo "⚠️  Teams Test Tool not found at: $(TEAMS_TEST_TOOL)"; \
	    echo "   To install: cd $(TEAMS_DIR) && npm install @microsoft/teams-app-test-tool"; \
	fi

####################
# UTILITY COMMANDS
####################

stop: ## Stop all services
	@echo "🛑 Stopping all services..."
	@pkill -f "langgraph dev" 2>/dev/null || true
	@pkill -f "uvicorn app:app" 2>/dev/null || true
	@pkill -f "python app.py" 2>/dev/null || true
	@pkill -f "teams-app-test-tool" 2>/dev/null || true
	@pkill -f "@microsoft/teams-app-test-tool" 2>/dev/null || true
	@if command -v fuser >/dev/null 2>&1; then \
	    fuser -k $(LANGGRAPH_PORT)/tcp 2>/dev/null || true; \
	    fuser -k $(BACKEND_PORT)/tcp 2>/dev/null || true; \
	    fuser -k $(TEAMS_PORT)/tcp 2>/dev/null || true; \
	fi
	@echo "✅ All services stopped"

cleanup-ports: ## Clean up ports used by services
	@echo "🧹 Cleaning up ports..."
	@if command -v fuser >/dev/null 2>&1; then \
	    fuser -k $(LANGGRAPH_PORT)/tcp 2>/dev/null || true; \
	    fuser -k $(BACKEND_PORT)/tcp 2>/dev/null || true; \
	    fuser -k $(TEAMS_PORT)/tcp 2>/dev/null || true; \
	fi
	@sleep 2

status: ## Check status of all services
	@echo "📊 Service Status:"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@if command -v ss >/dev/null 2>&1; then \
	    if ss -tuln 2>/dev/null | grep -q ":$(LANGGRAPH_PORT) "; then \
	        echo "   ✅ LangGraph Server: http://localhost:$(LANGGRAPH_PORT)"; \
	    else \
	        echo "   ❌ LangGraph Server: Not running"; \
	    fi; \
	    if ss -tuln 2>/dev/null | grep -q ":$(BACKEND_PORT) "; then \
	        echo "   ✅ Backend API:      http://localhost:$(BACKEND_PORT)"; \
	    else \
	        echo "   ❌ Backend API:      Not running"; \
	    fi; \
	    if ss -tuln 2>/dev/null | grep -q ":$(TEAMS_PORT) "; then \
	        echo "   ✅ Teams Bot:        http://localhost:$(TEAMS_PORT)"; \
	    else \
	        echo "   ❌ Teams Bot:        Not running"; \
	    fi; \
	else \
	    echo "   ℹ️  Install 'ss' command for port checking"; \
	fi
	@echo "   📖 API Docs:         http://localhost:$(BACKEND_PORT)/docs"
	@if [ -f "$(TEAMS_TEST_TOOL)" ]; then \
	    echo "   🧪 Teams Test Tool:  Available"; \
	else \
	    echo "   ⚠️  Teams Test Tool:  Not installed"; \
	fi

wait-for-langgraph: ## Wait for LangGraph to start
	@echo "⏳ Waiting for LangGraph server..."
	@for i in $$(seq 1 30); do \
	    if command -v ss >/dev/null 2>&1 && ss -tuln 2>/dev/null | grep -q ":$(LANGGRAPH_PORT) "; then \
	        echo "✅ LangGraph server is running"; \
	        break; \
	    fi; \
	    sleep 2; \
	    echo "   ... waiting ($$i/30)"; \
	done

wait-for-backend: ## Wait for Backend to start
	@echo "⏳ Waiting for Backend API..."
	@for i in $$(seq 1 15); do \
	    if command -v ss >/dev/null 2>&1 && ss -tuln 2>/dev/null | grep -q ":$(BACKEND_PORT) "; then \
	        echo "✅ Backend API is running"; \
	        break; \
	    fi; \
	    sleep 2; \
	    echo "   ... waiting ($$i/15)"; \
	done

wait-for-teams: ## Wait for Teams bot to start
	@echo "⏳ Waiting for Teams bot..."
	@for i in $$(seq 1 10); do \
	    if command -v ss >/dev/null 2>&1 && ss -tuln 2>/dev/null | grep -q ":$(TEAMS_PORT) "; then \
	        echo "✅ Teams bot is running"; \
	        break; \
	    fi; \
	    sleep 2; \
	    echo "   ... waiting ($$i/10)"; \
	done

check-deps: ## Check if required dependencies exist
	@echo "🔧 Checking dependencies..."
	@for dir in main backend teams; do \
	    if [ ! -d "$(PROJECT_ROOT)/$$dir" ]; then \
	        echo "❌ Directory $$dir not found!"; \
	        exit 1; \
	    fi; \
	done
	@echo "✅ All directories found"
	@if [ -f "$(TEAMS_TEST_TOOL)" ]; then \
	    echo "✅ Teams Test Tool found"; \
	else \
	    echo "⚠️  Teams Test Tool not found - install with: cd teams && npm install @microsoft/teams-app-test-tool"; \
	fi

test-services: ## Test all service endpoints
	@echo "🧪 Testing service endpoints..."
	@echo "Testing LangGraph..."
	@curl -s http://localhost:$(LANGGRAPH_PORT)/health > /dev/null && echo "✅ LangGraph OK" || echo "❌ LangGraph failed"
	@echo "Testing Backend..."
	@curl -s http://localhost:$(BACKEND_PORT)/health > /dev/null && echo "✅ Backend OK" || echo "❌ Backend failed"
	@echo "Testing Teams Bot..."
	@curl -s http://localhost:$(TEAMS_PORT)/health > /dev/null && echo "✅ Teams Bot OK" || echo "❌ Teams Bot failed"

install-deps: ## Install dependencies for all services
	@echo "📦 Installing dependencies..."
	@cd $(MAIN_DIR) && pip install -e .
	@cd $(BACKEND_DIR) && pip install -r requirements.txt 2>/dev/null || echo "No requirements.txt found"
	@cd $(TEAMS_DIR) && pip install -r requirements.txt 2>/dev/null || echo "No requirements.txt found"
	@echo "✅ Dependencies installed"

install-test-tool: ## Install Teams App Test Tool
	@echo "📥 Installing Teams App Test Tool..."
	@cd $(TEAMS_DIR) && npm install @microsoft/teams-app-test-tool
	@echo "✅ Teams App Test Tool installed"

clean: stop ## Stop services and clean up
	@echo "🧹 Cleaning up..."
	@rm -f $(MAIN_DIR)/*.log $(BACKEND_DIR)/*.log $(TEAMS_DIR)/*.log 2>/dev/null || true
	@echo "✅ Cleanup complete"

restart: stop start ## Restart all services

dev: ## Start in development mode (with auto-reload)
	@echo "🔧 Starting in development mode..."
	@$(MAKE) start

####################
# HELP
####################

help: ## Show this help message
	@echo "DOCX Agent - Multi-Service Startup"
	@echo "=================================="
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Main Commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Service URLs:"
	@echo "  LangGraph Server: http://localhost:$(LANGGRAPH_PORT)"
	@echo "  Backend API:      http://localhost:$(BACKEND_PORT)"
	@echo "  Teams Bot:        http://localhost:$(TEAMS_PORT)"
	@echo "  API Docs:         http://localhost:$(BACKEND_PORT)/docs"
	@echo ""
	@echo "Teams Test Tool:"
	@echo "  Install:          make install-test-tool"
	@echo "  Start manually:   cd teams && node devTools/teamsapptester/node_modules/@microsoft/teams-app-test-tool/cli.js start"
	@echo ""
	@echo "Examples:"
	@echo "  make start        # Start all services"
	@echo "  make status       # Check service status"
	@echo "  make stop         # Stop all services"
	@echo "  make restart      # Restart all services"
	@echo "  make test-services # Test all endpoints"