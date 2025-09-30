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
from pathlib import Path

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
    platform: str = "api"  # api, telegram, discord, slack, whatsapp,teams
    metadata: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Standard response format"""
    user_id: str
    message: str
    platform: str = "api"
    requires_approval: bool = False
    approval_data: Optional[Dict[str, Any]] = None
    session_id: str
    metadata: Optional[Dict[str, Any]] = {}
    status: str = "completed"  # completed, waiting_approval, error


class ApprovalRequest(BaseModel):
    """Approval response from user"""
    user_id: str
    session_id: str
    approved: bool
    platform: str = "api"
    user_profile: Optional[Dict[str, Any]] = {}


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
        
        user_profile = {}
        enhanced_message = message.message
        
        if message.metadata:
            user_profile = message.metadata.get("user_profile", {})
            
            if user_profile.get("name"): 
                enhanced_message = f"[User: {user_profile['name']}] {message.message}"
                logger.info(f"Processing message for user: {user_profile['name']}")
        
        if user_profile: 
            session.metadata = session.metadata or {}
            session.metadata["user_profile"] = user_profile
        
        if message.message.startswith("/load "):
            filename = message.message.replace("/load ", "").strip()
            file_path = load_test_document(filename)
            
            response_metadata = {}
            if user_profile:
                response_metadata["user_profile"] = user_profile
            
            if file_path:
                # Store the document path in session metadata
                session.metadata = session.metadata or {}
                session.metadata["document_path"] = file_path
                session.metadata["document_name"] = filename
                
                return ChatResponse(
                    user_id=message.user_id,
                    message=f"✅ Document '{filename}' loaded successfully!\n\n"
                            f"📍 Location: {file_path}\n\n"
                            f"You can now:\n"
                            f"• Ask me to summarize the document\n"
                            f"• Search for content\n"
                            f"• Request document structure\n"
                            f"• Edit content (with approval)",
                    platform=message.platform,
                    requires_approval=False,
                    session_id=session.session_id,
                    metadata=response_metadata,
                    status="completed"
                )
            else:
                return ChatResponse(
                    user_id=message.user_id,
                    message=f"❌ Document '{filename}' not found.\n\n"
                            f"Please make sure the file exists in one of these locations:\n"
                            f"• /home/aditya/work/temp/DOCX-agent/backend/\n"
                            f"• /home/aditya/work/temp/DOCX-agent/\n"
                            f"• /home/aditya/work/temp/DOCX-agent/main/",
                    platform=message.platform,
                    requires_approval=False,
                    session_id=session.session_id,
                    metadata=response_metadata,
                    status="error"
                )
        
        if session.pending_approval and message.message.lower() in ['yes', 'no', '/approve', '/reject']:
            approval_response = ApprovalRequest(
                user_id=message.user_id,
                session_id=session.session_id,
                approved=message.message.lower() in ['yes', '/approve'],
                platform=message.platform,
                user_profile=user_profile
            )
            
            try:
                # Process the approval
                session = session_manager.get_session(approval_response.session_id)
                if not session:
                    raise HTTPException(status_code=404, detail="Session not found")
                
                if not session.pending_approval:
                    return ChatResponse(
                        user_id=message.user_id,
                        message="No pending approval found.",
                        platform=message.platform,
                        requires_approval=False,
                        session_id=session.session_id,
                        status="error"
                    )
                
                # Resume agent with approval decision
                result = await agent_runner.resume_with_approval(
                    session_id=approval_response.session_id,
                    thread_id=session.thread_id,
                    approved=approval_response.approved
                )
                
                # Clear pending approval
                session_manager.clear_pending_approval(approval_response.session_id)
                
                response_metadata = {}
                if user_profile:
                    response_metadata["user_profile"] = user_profile
                
                return ChatResponse(
                    user_id=message.user_id,
                    message=result["message"],
                    platform=message.platform,
                    requires_approval=False,
                    session_id=session.session_id,
                    metadata=response_metadata,
                    status="completed"
                )
                
            except Exception as e:
                logger.error(f"Error processing approval: {str(e)}", exc_info=True)
                return ChatResponse(
                    user_id=message.user_id,
                    message="Sorry, there was an error processing your approval. Please try again.",
                    platform=message.platform,
                    requires_approval=False,
                    session_id=session.session_id,
                    status="error"
                )
                
        # Check if user has a pending approval
        if session.pending_approval:
            return ChatResponse(
                user_id=message.user_id,
                message="You have a pending approval request. Please respond with /approve or /reject first.",
                platform=message.platform,
                requires_approval=False,
                session_id=session.session_id,
                status="error"
            )
        
        # Run the agent
        document_context = {}
        if session.metadata and session.metadata.get("document_path"):
            document_context = {
                "document_path": session.metadata["document_path"],
                "document_name": session.metadata.get("document_name", "unknown"),
                "loaded": True
            }
            
            # Create a more explicit message for the agent
            doc_info = (
                f"\n\nDOCUMENT CONTEXT:\n"
                f"- Document loaded: {session.metadata['document_name']}\n"
                f"- File path: {session.metadata['document_path']}\n"
                f"- Status: Ready for processing\n"
                f"- User request: {enhanced_message}\n"
                f"\nPlease process this request using the loaded document."
            )
            enhanced_message = doc_info
        else:
            document_context = {}
        
        result = await agent_runner.process_message(
            session_id=session.session_id,
            thread_id=session.thread_id,
            message=enhanced_message,
            document_context=document_context
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
            
            response_metadata = {}
            if user_profile:
                response_metadata["user_profile"] = user_profile
            
            return ChatResponse(
                user_id=message.user_id,
                message=approval_msg,
                platform=message.platform,
                requires_approval=True,
                approval_data=result["approval_data"],
                session_id=session.session_id,
                metadata=response_metadata,
                status="waiting_approval"
            )
            
        response_metadata = {}
        if user_profile:
            response_metadata["user_profile"] = user_profile
        
        # Normal response
        return ChatResponse(
            user_id=message.user_id,
            message=result["message"],
            platform=message.platform,
            requires_approval=False,
            session_id=session.session_id,
            metadata=response_metadata,
            status="completed"
        )
        
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}", exc_info=True)
        return ChatResponse(
            user_id=message.user_id,
            message="Sorry, I encountered an error processing your request. Please try again.",
            platform=message.platform,
            requires_approval=False,
            session_id=session.session_id if 'session' in locals() else str(uuid.uuid4()),
            status="error"
        )


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
                user_id=approval.user_id,
                message="No pending approval found.",
                platform=approval.platform,
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
        
        response_metadata = {}
        if approval.user_profile:
            response_metadata["user_profile"] = approval.user_profile
            
        
        return ChatResponse(
            user_id=approval.user_id,
            message=result["message"],
            platform=approval.platform,
            requires_approval=False,
            session_id=session.session_id,
            metadata=response_metadata,
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

@app.get("/api/debug/session/{user_id}")
async def debug_session(user_id: str):
    """Debug endpoint to see session state"""
    session = session_manager.get_or_create_session(user_id, "debug")
    return {
        "session_id": session.session_id,
        "user_id": session.user_id,
        "pending_approval": session.pending_approval,
        "metadata": session.metadata,
        "created_at": session.created_at,
        "last_activity": session.last_activity
    }

@app.post("/api/debug/clear-session/{user_id}")
async def clear_session(user_id: str):
    """Clear session state for debugging"""
    sessions = session_manager.get_user_sessions(user_id)
    for session in sessions:
        session_manager.clear_pending_approval(session.session_id)
    return {"message": f"Cleared session state for {user_id}"}

# Add this endpoint after the debug endpoints:
@app.post("/api/test-document")
async def test_document_processing():
    """Test document processing directly"""
    try:
        # Find a test document
        doc_path = load_test_document("master.docx")
        if not doc_path:
            return {"error": "No test document found"}
        
        # Try to process it directly
        try:
            import docx2python
            doc = docx2python.docx2python(doc_path)
            text_content = doc.text
            
            return {
                "document_path": doc_path,
                "content_length": len(text_content),
                "first_100_chars": text_content[:100],
                "status": "success",
                "file_exists": True
            }
        except ImportError:
            # Try with python-docx
            from docx import Document
            doc = Document(doc_path)
            text_content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            
            return {
                "document_path": doc_path,
                "content_length": len(text_content),
                "first_100_chars": text_content[:100],
                "status": "success (python-docx)",
                "file_exists": True
            }
            
    except Exception as e:
        return {"error": str(e), "status": "failed"}
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


def load_test_document(filename: str = None):
    """Load a test document for development"""
    if filename:
        # Look for the specific file in common locations
        possible_paths = [
            os.path.join(os.path.dirname(__file__), filename),
            os.path.join(os.path.dirname(__file__), "..", filename),
            os.path.join(os.path.dirname(__file__), "..", "main", filename),
            os.path.join(os.path.dirname(__file__), "..", "documents", filename),
            f"/home/aditya/work/temp/DOCX-agent/{filename}",
            f"/home/aditya/work/temp/DOCX-agent/backend/{filename}",
            f"/home/aditya/work/temp/DOCX-agent/main/{filename}",
        ]
    else:
        # Look for any DOCX file
        possible_paths = [
            "/home/aditya/work/temp/DOCX-agent/backend/master.docx",
            "/home/aditya/work/temp/DOCX-agent/master.docx",
            "/home/aditya/work/temp/DOCX-agent/main/master.docx",
        ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

# ============================================================================
# Run Server
# ============================================================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
