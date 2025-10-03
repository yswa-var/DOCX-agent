"""DOCX-specific nodes for the agent workflow."""

from datetime import UTC, datetime
from typing import Any, Dict, List, Literal

from langchain_core.messages import AIMessage, ToolMessage
from langgraph.prebuilt import ToolNode
from langgraph.runtime import Runtime
from langgraph.types import interrupt

from react_agent.context import Context
from react_agent.state import State
from react_agent.tools import TOOLS
from react_agent.utils import load_chat_model


async def docx_logic(
    state: State, runtime: Runtime[Context]
) -> Dict[str, List[AIMessage]]:
    """DOCX-specific logic node for document manipulation reasoning.
    
    This node handles the reasoning and decision-making for DOCX document
    operations, including reading, searching, and planning edits.
    
    Args:
        state (State): The current state of the conversation.
        runtime (Runtime[Context]): Runtime context containing configuration.

    Returns:
        dict: A dictionary containing the model's response message.
    """
    try:
        # Initialize the model with DOCX tools
        model = load_chat_model(runtime.context.model).bind_tools(TOOLS)

        # Format the system prompt with DOCX-specific context
        system_message = runtime.context.system_prompt.format(
            system_time=datetime.now(tz=UTC).isoformat()
        )

        # Get the model's response focused on DOCX operations
        response = await model.ainvoke(
            [{"role": "system", "content": system_message}, *state.messages]
        )

        # Ensure we got an AIMessage
        if not isinstance(response, AIMessage):
            raise ValueError(f"Model returned {type(response).__name__}, expected AIMessage")

        # Handle the case when it's the last step and the model still wants to use a tool
        if state.is_last_step and response.tool_calls:
            return {
                "messages": [
                    AIMessage(
                        id=response.id,
                        content="I've reached the maximum number of steps for this DOCX operation. Please try a more specific request.",
                    )
                ]
            }

        return {"messages": [response]}
    
    except Exception as e:
        # If there's an error, return an error message as AIMessage
        error_message = AIMessage(
            content=f"An error occurred while processing DOCX logic: {str(e)}"
        )
        return {"messages": [error_message]}


def docx_tools() -> ToolNode:
    """Create a ToolNode specifically for DOCX operations.
    
    Returns:
        ToolNode: Configured tool node for DOCX document manipulation
    """
    return ToolNode(TOOLS)


# List of tools that require human approval (write operations)
WRITE_TOOLS = {"apply_edit"}  # Add more write tools here as needed


def requires_approval(tool_name: str) -> bool:
    """Check if a tool requires human approval.
    
    Args:
        tool_name: Name of the tool being called
        
    Returns:
        True if the tool requires approval, False otherwise
    """
    return tool_name in WRITE_TOOLS


async def approval_node(state: State) -> Dict[str, Any]:
    """Request human approval for critical DOCX operations.
    
    This node pauses execution and asks for human approval before
    executing write operations on the document.
    
    Args:
        state (State): The current state of the conversation.
        
    Returns:
        dict: Updated state with approved operation or rejection message.
    """
    last_message = state.messages[-1]
    
    if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
        return {}
    
    # Check if any tool calls require approval
    tool_calls_needing_approval = [
        tc for tc in last_message.tool_calls 
        if requires_approval(tc["name"])
    ]
    
    if not tool_calls_needing_approval:
        # No approval needed, proceed to tools
        return {}
    
    # For now, handle the first tool call that needs approval
    tool_call = tool_calls_needing_approval[0]
    tool_name = tool_call["name"]
    tool_args = tool_call["args"]
    
    # Create a human-readable description of the operation
    if tool_name == "apply_edit":
        anchor = tool_args.get("anchor", [])
        new_text = tool_args.get("new_text", "")
        description = (
            f"**DOCX Edit Operation**\n"
            f"- Location: {anchor}\n"
            f"- New text: {new_text[:100]}{'...' if len(new_text) > 100 else ''}\n\n"
            f"Do you approve this DOCX change? (yes/no)"
        )
    else:
        description = f"Approve DOCX {tool_name} operation with args: {tool_args}? (yes/no)"
    
    # Interrupt and wait for human approval
    approval = interrupt(
        {
            "type": "docx_approval_request",
            "tool_name": tool_name,
            "tool_call_id": tool_call["id"],
            "args": tool_args,
            "description": description
        }
    )
    
    # Process approval response
    if isinstance(approval, str):
        approval = approval.lower().strip()
    
    if approval in ["yes", "y", "approve", "approved", "true"]:
        # Approval granted - proceed with the operation
        return {"pending_operation": None}
    else:
        # Approval denied - create tool messages for all tool calls
        tool_messages = []
        
        for tc in last_message.tool_calls:
            if tc["id"] == tool_call["id"]:
                # This is the rejected tool
                tool_messages.append(ToolMessage(
                    content=f"DOCX operation cancelled by user. The {tc['name']} operation was not executed.",
                    tool_call_id=tc["id"],
                    name=tc["name"]
                ))
            else:
                # Other tool calls should also get rejection messages
                tool_messages.append(ToolMessage(
                    content=f"Skipped due to user rejection of DOCX {tool_name}.",
                    tool_call_id=tc["id"],
                    name=tc["name"]
                ))
        
        return {
            "messages": tool_messages,
            "pending_operation": None
        }


def route_docx_output(state: State) -> Literal["__end__", "docx_tools", "approval_node"]:
    """Determine the next node based on the DOCX model's output.

    This function checks if the model's last message contains tool calls
    and routes to approval if needed for DOCX operations.

    Args:
        state (State): The current state of the conversation.

    Returns:
        str: The name of the next node to call.
    """
    last_message = state.messages[-1]
    
    # Ensure we have an AIMessage
    if not isinstance(last_message, AIMessage):
        raise ValueError(
            f"Expected AIMessage in DOCX output edges, but got {type(last_message).__name__}. "
            f"This indicates the docx_logic function did not return an AIMessage."
        )
    
    # If there is no tool call, then we finish
    if not last_message.tool_calls:
        return "__end__"
    
    # Check if any tool calls require approval
    needs_approval = any(
        requires_approval(tc["name"]) for tc in last_message.tool_calls
    )
    
    if needs_approval:
        return "approval_node"
    
    # No approval needed, execute DOCX tools directly
    return "docx_tools"


def route_docx_approval(state: State) -> Literal["docx_tools", "docx_logic"]:
    """Route after DOCX approval node.
    
    If approval was granted, go to tools. If rejected, go back to docx_logic.
    
    Args:
        state (State): The current state.
        
    Returns:
        str: Next node to call.
    """
    # Check if the last message is a rejection (ToolMessage added by approval_node)
    if state.messages and isinstance(state.messages[-1], ToolMessage):
        # Rejection message was added, go back to docx_logic
        return "docx_logic"
    
    # Approval granted, proceed to execute DOCX tools
    return "docx_tools"
