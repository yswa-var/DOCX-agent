"""Define a custom Reasoning and Action agent.

Works with a chat model with tool calling support.
"""

from datetime import UTC, datetime
from typing import Dict, List, Literal, cast

from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.runtime import Runtime

from react_agent.context import Context
from react_agent.state import InputState, State
from react_agent.tools import TOOLS
from react_agent.utils import load_chat_model

# Define the function that calls the model


async def call_model(
    state: State, runtime: Runtime[Context]
) -> Dict[str, List[AIMessage]]:
    """Call the LLM powering our "agent".

    This function prepares the prompt, initializes the model, and processes the response.

    Args:
        state (State): The current state of the conversation.
        runtime (Runtime[Context]): Runtime context containing configuration.

    Returns:
        dict: A dictionary containing the model's response message.
    """
    try:
        # Initialize the model with tool binding. Change the model or add more tools here.
        model = load_chat_model(runtime.context.model).bind_tools(TOOLS)

        # Format the system prompt. Customize this to change the agent's behavior.
        system_message = runtime.context.system_prompt.format(
            system_time=datetime.now(tz=UTC).isoformat()
        )

        # Get the model's response
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
                        content="Sorry, I could not find an answer to your question in the specified number of steps.",
                    )
                ]
            }

        # Return the model's response as a list to be added to existing messages
        return {"messages": [response]}
    
    except Exception as e:
        # If there's an error, return an error message as AIMessage
        error_message = AIMessage(
            content=f"An error occurred while calling the model: {str(e)}"
        )
        return {"messages": [error_message]}


# Define a new graph

builder = StateGraph(State, input_schema=InputState, context_schema=Context)

# Define the two nodes we will cycle between
builder.add_node(call_model)
builder.add_node("tools", ToolNode(TOOLS))

# Set the entrypoint as `call_model`
# This means that this node is the first one called
builder.add_edge("__start__", "call_model")


def route_model_output(state: State) -> Literal["__end__", "tools"]:
    """Determine the next node based on the model's output.

    This function checks if the model's last message contains tool calls.

    Args:
        state (State): The current state of the conversation.

    Returns:
        str: The name of the next node to call ("__end__" or "tools").
    """
    last_message = state.messages[-1]
    
    # Ensure we have an AIMessage - this should always be the case after call_model
    if not isinstance(last_message, AIMessage):
        raise ValueError(
            f"Expected AIMessage in output edges, but got {type(last_message).__name__}. "
            f"This indicates the call_model function did not return an AIMessage."
        )
    
    # If there is no tool call, then we finish
    if not last_message.tool_calls:
        return "__end__"
    # Otherwise we execute the requested actions
    return "tools"


# Add a conditional edge to determine the next step after `call_model`
builder.add_conditional_edges(
    "call_model",
    # After call_model finishes running, the next node(s) are scheduled
    # based on the output from route_model_output
    route_model_output,
)

# Add a normal edge from `tools` to `call_model`
# This creates a cycle: after using tools, we always return to the model
builder.add_edge("tools", "call_model")

# Compile the builder into an executable graph
graph = builder.compile(name="ReAct Agent")
