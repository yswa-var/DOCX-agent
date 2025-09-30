"""
FastAPI Backend for LangGraph DOCX Agent Bot
Enables the agent to be used across multiple chat platforms
"""

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn
import logging
from datetime import datetime
import uuid
import os

from session_manager import SessionManager
from agent_runner import AgentRunner

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="DOCX Agent Bot API",
    description="Multi-platform bot backend for LangGraph DOCX Agent",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
# CSV file will be created in the backend directory
csv_path = os.getenv("SESSIONS_CSV_PATH", "sessions.csv")
session_manager = SessionManager(csv_file=csv_path)
agent_runner = AgentRunner()


# ============================================================================
# Request/Response Models
# ============================================================================

class ChatMessage(BaseModel):
    """Standard chat message format"""
    user_id: str
    message: str
    platform: str = "api"  # api, telegram, discord, slack, whatsapp
    metadata: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Standard response format"""
    message: str
    requires_approval: bool = False
    approval_data: Optional[Dict[str, Any]] = None
    session_id: str
    status: str = "completed"  # completed, waiting_approval, error


class ApprovalRequest(BaseModel):
    """Approval response from user"""
    user_id: str
    session_id: str
    approved: bool
    platform: str = "api"


# ============================================================================
# Health Check & Info
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "DOCX Agent Bot API",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "chat": "/api/chat",
            "approve": "/api/approve",
            "sessions": "/api/sessions",
            "webhooks": {
            }
        },
        "documentation": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "active_sessions": session_manager.get_active_session_count()
    }


# ============================================================================
# Core Chat API
# ============================================================================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """
    Main chat endpoint for all platforms
    
    This endpoint:
    1. Receives a message from any platform
    2. Routes it to the LangGraph agent
    3. Handles approval flows if needed
    4. Returns a response
    """
    try:
        logger.info(f"Received message from {message.user_id} on {message.platform}")
        
        # Get or create session
        session = session_manager.get_or_create_session(
            user_id=message.user_id,
            platform=message.platform
        )
        
        # Check if user has a pending approval
        if session.pending_approval:
            return ChatResponse(
                message="You have a pending approval request. Please respond with /approve or /reject first.",
                requires_approval=False,
                session_id=session.session_id,
                status="error"
            )
        
        # Run the agent
        result = await agent_runner.process_message(
            session_id=session.session_id,
            thread_id=session.thread_id,
            message=message.message
        )
        
        # Check if approval is required
        if result.get("requires_approval"):
            # Store approval data in session
            session_manager.set_pending_approval(
                session_id=session.session_id,
                approval_data=result["approval_data"]
            )
            
            # Format approval message for user
            approval_msg = format_approval_message(result["approval_data"])
            
            return ChatResponse(
                message=approval_msg,
                requires_approval=True,
                approval_data=result["approval_data"],
                session_id=session.session_id,
                status="waiting_approval"
            )
        
        # Normal response
        return ChatResponse(
            message=result["message"],
            requires_approval=False,
            session_id=session.session_id,
            status="completed"
        )
        
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/approve")
async def approve(approval: ApprovalRequest):
    """
    Handle approval/rejection from user
    
    When a user responds to an approval request, this endpoint:
    1. Retrieves the pending operation
    2. Resumes the agent with approval/rejection
    3. Returns the final result
    """
    try:
        logger.info(f"Approval response from {approval.user_id}: {approval.approved}")
        
        # Get session
        session = session_manager.get_session(approval.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Check if there's a pending approval
        if not session.pending_approval:
            return ChatResponse(
                message="No pending approval found.",
                requires_approval=False,
                session_id=session.session_id,
                status="error"
            )
        
        # Resume agent with approval decision
        result = await agent_runner.resume_with_approval(
            session_id=session.session_id,
            thread_id=session.thread_id,
            approved=approval.approved
        )
        
        # Clear pending approval
        session_manager.clear_pending_approval(approval.session_id)
        
        return ChatResponse(
            message=result["message"],
            requires_approval=False,
            session_id=session.session_id,
            status="completed"
        )
        
    except Exception as e:
        logger.error(f"Error processing approval: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Session Management
# ============================================================================

@app.get("/api/sessions/{user_id}")
async def get_user_sessions(user_id: str):
    """Get all sessions for a user"""
    sessions = session_manager.get_user_sessions(user_id)
    return {
        "user_id": user_id,
        "sessions": [s.to_dict() for s in sessions]
    }


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    success = session_manager.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "deleted", "session_id": session_id}


@app.get("/api/sessions")
async def list_all_sessions():
    """List all active sessions (admin endpoint)"""
    return {
        "active_sessions": session_manager.get_all_sessions(),
        "count": session_manager.get_active_session_count()
    }


# ============================================================================
# Helper Functions
# ============================================================================

def format_approval_message(approval_data: Dict[str, Any]) -> str:
    """Format approval request for user-friendly display"""
    tool_name = approval_data.get("tool_name", "unknown")
    description = approval_data.get("description", "")
    
    message = f"""
🔔 **Approval Required**

{description}

Reply with:
• `/approve` or `yes` to proceed
• `/reject` or `no` to cancel
"""
    return message.strip()


# ============================================================================
# Run Server
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
