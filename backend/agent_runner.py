"""
Agent Runner - Handles communication with LangGraph agent
"""

import sys
import os
from typing import Dict, Any, Optional, List
import asyncio
import logging

# Add the main directory to Python path to import the agent
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'main', 'src'))

from langgraph_sdk import get_client
from langgraph_sdk.schema import Command

logger = logging.getLogger(__name__)


class AgentRunner:
    """Handles running the LangGraph agent and managing conversations"""
    
    def __init__(self, langgraph_url: Optional[str] = None):
        """
        Initialize agent runner
        
        Args:
            langgraph_url: URL of LangGraph server (defaults to local)
        """
        self.langgraph_url = langgraph_url or os.getenv(
            "LANGGRAPH_URL", 
            "http://localhost:8123"
        )
        self.assistant_id = "docx_agent"
        self._client = None
        self._use_remote = langgraph_url is not None
        
        # If using remote LangGraph server
        if self._use_remote:
            self._init_remote_client()
        else:
            # Use local graph import
            self._init_local_graph()
    
    def _init_remote_client(self):
        """Initialize remote LangGraph client"""
        try:
            self._client = get_client(url=self.langgraph_url)
            logger.info(f"Connected to LangGraph server at {self.langgraph_url}")
        except Exception as e:
            logger.warning(f"Failed to connect to LangGraph server: {e}")
            logger.info("Falling back to local graph execution")
            self._init_local_graph()
    
    def _init_local_graph(self):
        """Initialize local graph for direct execution"""
        try:
            from react_agent.graph import builder
            from react_agent.context import Context
            from langgraph.checkpoint.memory import MemorySaver
            
            # Create checkpointer for state management
            self._checkpointer = MemorySaver()
            
            # Compile graph with checkpointer to enable interrupts
            self._graph = builder.compile(
                checkpointer=self._checkpointer,
                name="ReAct Agent"
            )
            self._use_remote = False
            
            # Store default context
            self._default_context = Context()
            
            logger.info("Using local graph execution with checkpointer")
        except ImportError as e:
            logger.error(f"Failed to import local graph: {e}")
            raise RuntimeError("Cannot initialize agent - no local or remote graph available")
    
    async def process_message(
        self, 
        session_id: str,
        thread_id: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Process a user message through the agent
        
        Args:
            session_id: Session identifier
            thread_id: LangGraph thread ID for conversation continuity
            message: User's message
            
        Returns:
            Dict containing response and approval status
        """
        try:
            if self._use_remote:
                return await self._process_remote(thread_id, message)
            else:
                return await self._process_local(thread_id, message)
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return {
                "message": f"Sorry, I encountered an error: {str(e)}",
                "requires_approval": False,
                "error": str(e)
            }
    
    async def _process_remote(self, thread_id: str, message: str) -> Dict[str, Any]:
        """Process message using remote LangGraph server"""
        # Run the agent
        result = await self._client.runs.wait(
            thread_id,
            self.assistant_id,
            input={
                "messages": [{"role": "user", "content": message}]
            }
        )
        
        # Check for interrupts (approval requests)
        if "__interrupt__" in result and result["__interrupt__"]:
            interrupt = result["__interrupt__"][0]
            approval_data = interrupt.get("value", {})
            
            return {
                "message": approval_data.get("description", "Approval required"),
                "requires_approval": True,
                "approval_data": approval_data
            }
        
        # Extract the last message from the agent
        messages = result.get("messages", [])
        if messages:
            last_message = messages[-1]
            content = last_message.get("content", "No response")
            
            return {
                "message": content,
                "requires_approval": False
            }
        
        return {
            "message": "No response from agent",
            "requires_approval": False
        }
    
    async def _process_local(self, thread_id: str, message: str) -> Dict[str, Any]:
        """Process message using local graph"""
        from langchain_core.messages import HumanMessage, AIMessage
        
        # Create config with thread_id for checkpointing
        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }
        
        # Prepare input
        input_data = {
            "messages": [HumanMessage(content=message)]
        }
        
        # Run the graph
        try:
            # Invoke the graph - it will stop at interrupts
            result = await self._graph.ainvoke(
                input_data,
                config=config,
                context=self._default_context
            )
            
            # Check if execution was interrupted (approval needed)
            state = await self._graph.aget_state(config)
            
            # Check if there are pending tasks (interrupts)
            if state.next:  # next contains the nodes that are pending
                # There's an interrupt - check for approval data
                # The interrupt data is stored in state.tasks
                if state.tasks:
                    for task in state.tasks:
                        if task.interrupts:
                            # Found an interrupt
                            interrupt_data = task.interrupts[0]
                            approval_data = interrupt_data.value
                            
                            return {
                                "message": approval_data.get("description", "Approval required"),
                                "requires_approval": True,
                                "approval_data": approval_data
                            }
            
            # No interrupt - extract the response message
            if result and "messages" in result:
                messages = result["messages"]
                if messages:
                    last_message = messages[-1]
                    if isinstance(last_message, AIMessage):
                        return {
                            "message": last_message.content,
                            "requires_approval": False
                        }
            
            return {
                "message": "Processed successfully",
                "requires_approval": False
            }
            
        except Exception as e:
            logger.error(f"Error in local graph execution: {e}", exc_info=True)
            raise
    
    async def resume_with_approval(
        self,
        session_id: str,
        thread_id: str,
        approved: bool
    ) -> Dict[str, Any]:
        """
        Resume agent execution after approval decision
        
        Args:
            session_id: Session identifier
            thread_id: LangGraph thread ID
            approved: Whether the operation was approved
            
        Returns:
            Dict containing the final response
        """
        try:
            from langgraph.types import Command
            from langchain_core.messages import AIMessage
            
            approval_response = "yes" if approved else "no"
            
            if self._use_remote:
                # Resume using Command
                result = await self._client.runs.wait(
                    thread_id,
                    self.assistant_id,
                    command=Command(resume=approval_response)
                )
                
                # Extract response
                messages = result.get("messages", [])
                if messages:
                    last_message = messages[-1]
                    content = last_message.get("content", "Operation completed")
                    
                    return {
                        "message": content,
                        "requires_approval": False
                    }
            else:
                # For local execution, resume from interrupt with approval response
                config = {
                    "configurable": {
                        "thread_id": thread_id
                    }
                }
                
                # Resume the graph execution with the approval response
                result = await self._graph.ainvoke(
                    Command(resume=approval_response),
                    config=config,
                    context=self._default_context
                )
                
                # Extract the response
                if result and "messages" in result:
                    messages = result["messages"]
                    if messages:
                        last_message = messages[-1]
                        if isinstance(last_message, AIMessage):
                            return {
                                "message": last_message.content,
                                "requires_approval": False
                            }
                
                # Fallback response
                if approved:
                    return {
                        "message": "✅ Operation approved and executed successfully",
                        "requires_approval": False
                    }
                else:
                    return {
                        "message": "❌ Operation cancelled by user",
                        "requires_approval": False
                    }
            
        except Exception as e:
            logger.error(f"Error resuming with approval: {e}", exc_info=True)
            return {
                "message": f"Error processing approval: {str(e)}",
                "requires_approval": False,
                "error": str(e)
            }
