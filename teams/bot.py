import os
import json
import requests
from typing import Dict, Any, Optional
from botbuilder.core import ActivityHandler, TurnContext, MessageFactory, CardFactory
from botbuilder.schema import ChannelAccount, Activity, ActivityTypes, Attachment
from botbuilder.core.conversation_state import ConversationState
from botbuilder.core.user_state import UserState
from botbuilder.core.memory_storage import MemoryStorage
from botbuilder.core.conversation_state import ConversationState
from config import DefaultConfig
import logging

logger = logging.getLogger(__name__)

class DOCXAgentBot(ActivityHandler):
    def __init__(self, conversation_state: ConversationState, user_state: UserState):
        self.conversation_state = conversation_state
        self.user_state = user_state
        self.config = DefaultConfig()
        
        # Backend API configuration
        self.backend_url = os.getenv("BACKEND_API_URL", "http://localhost:8000")
        
    async def on_message_activity(self, turn_context: TurnContext):
        """Handle incoming messages"""
        user_id = turn_context.activity.from_property.id
        user_name = turn_context.activity.from_property.name
        message_text = turn_context.activity.text.strip()
        
        # Get user profile for memory
        user_profile = await self._get_user_profile(turn_context, user_id, user_name)
        
        try:
            
            if self._is_approval_response(message_text):
                response = await self._handle_approval(user_id, message_text, user_profile)
            else:
                
                response = await self._send_to_backend(user_id, message_text, user_profile)
            
            
            if response.get("requires_approval", False):
                await self._send_approval_message(turn_context, response)
            else:
                await turn_context.send_activity(MessageFactory.text(response["message"]))
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await turn_context.send_activity(
                MessageFactory.text("Sorry, I encountered an error. Please try again.")
            )
    
    async def on_members_added_activity(self, members_added: list, turn_context: TurnContext):
        """Greet new members"""
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                welcome_message = (
                    "👋 Hello! I'm your DOCX Document Agent.\n\n"
                    "I can help you:\n"
                    "• 📄 Index and analyze DOCX documents\n"
                    "• ✏️ Edit document content (with approval)\n"
                    "• 📋 Generate table of contents\n"
                    "• 🔍 Search through documents\n"
                    "• 📊 Get document outlines\n\n"
                    "Just upload a DOCX file or ask me what you'd like to do!"
                )
                await turn_context.send_activity(MessageFactory.text(welcome_message))
    
    async def _get_user_profile(self, turn_context: TurnContext, user_id: str, user_name: str) -> Dict[str, Any]:
        """Get or create user profile with memory"""
        user_state_accessor = self.user_state.create_property("UserProfile")
        user_profile = await user_state_accessor.get(turn_context, lambda: {})
        
      
        if not user_profile.get("initialized"):
            user_profile.update({
                "user_id": user_id,
                "name": user_name,
                "teams_id": user_id,
                "platform": "teams",
                "initialized": True,
                "preferences": {},
                "interaction_count": 0
            })
        
        
        user_profile["interaction_count"] = user_profile.get("interaction_count", 0) + 1
       
        await user_state_accessor.set(turn_context, user_profile)
        await self.user_state.save_changes(turn_context)
        
        return user_profile
    
    def _is_approval_response(self, message: str) -> bool:
      """Check if message is an approval response"""
      approval_keywords = ["yes", "no", "/approve", "/reject"]
      return message.lower().strip() in approval_keywords

    
    async def _handle_approval(self, user_id: str, message: str, user_profile: Dict) -> Dict[str, Any]:
      """Handle approval/rejection responses via chat endpoint"""
     
      return await self._send_to_backend(user_id, message, user_profile)
    
    async def _send_to_backend(self, user_id: str, message: str, user_profile: Dict) -> Dict[str, Any]:
        """Send message to FastAPI backend"""
        payload = {
            "user_id": f"teams_{user_id}",
            "message": message,
            "platform": "teams",
            "metadata": {
                "user_profile": user_profile,
                "teams_context": True
            }
        }
        
        response = requests.post(f"{self.backend_url}/api/chat", json=payload)
        response.raise_for_status()
        result = response.json()
      
        if result.get("requires_approval"):
            user_profile["pending_session_id"] = result.get("session_id")
        
        return result
    
    async def _send_approval_message(self, turn_context: TurnContext, response: Dict[str, Any]):
        """Send approval request with action buttons"""
        approval_card = self._create_approval_card(response)
        approval_attachment = MessageFactory.attachment(approval_card)
        await turn_context.send_activity(approval_attachment)
    
    def _create_approval_card(self, response: Dict[str, Any]) -> Attachment:
        """Create adaptive card for approval requests"""
        card_content = {
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "type": "AdaptiveCard",
            "version": "1.3",
            "body": [
                {
                    "type": "TextBlock",
                    "text": "🔔 Approval Required",
                    "weight": "Bolder",
                    "size": "Medium",
                    "color": "Attention"
                },
                {
                    "type": "TextBlock",
                    "text": response["message"],
                    "wrap": True,
                    "spacing": "Medium"
                }
            ],
            "actions": [
                {
                    "type": "Action.Submit",
                    "title": "✅ Approve",
                    "data": {
                        "action": "approve",
                        "session_id": response.get("session_id")
                    },
                    "style": "positive"
                },
                {
                    "type": "Action.Submit",
                    "title": "❌ Reject", 
                    "data": {
                        "action": "reject",
                        "session_id": response.get("session_id")
                    },
                    "style": "destructive"
                }
            ]
        }
        
        return CardFactory.adaptive_card(card_content)
    
    async def on_submit_action(self, turn_context: TurnContext):
        """Handle adaptive card submit actions"""
        action_data = turn_context.activity.value
        user_id = turn_context.activity.from_property.id
        
        if action_data.get("action") == "approve":
            message = "/approve"
        elif action_data.get("action") == "reject":
            message = "/reject"
        else:
            return
        
        user_profile = await self._get_user_profile(turn_context, user_id, turn_context.activity.from_property.name)
        
        # Process approval
        response = await self._handle_approval(user_id, message, user_profile)
        await turn_context.send_activity(MessageFactory.text(response["message"]))