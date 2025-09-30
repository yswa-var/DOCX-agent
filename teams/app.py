import os
import sys
import traceback
from datetime import datetime
from http import HTTPStatus
from pathlib import Path
from aiohttp import web
from aiohttp.web import Request, Response, json_response
from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    ConversationState,
    MemoryStorage,
    UserState,
)
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.schema import Activity, ActivityTypes

from bot import DOCXAgentBot
from config import DefaultConfig

# Create adapter
SETTINGS = BotFrameworkAdapterSettings(
    DefaultConfig.APP_ID,
    DefaultConfig.APP_PASSWORD,
    DefaultConfig.APP_TYPE,
    DefaultConfig.APP_TENANTID
)
ADAPTER = BotFrameworkAdapter(SETTINGS)

MEMORY = MemoryStorage()
CONVERSATION_STATE = ConversationState(MEMORY)
USER_STATE = UserState(MEMORY)

# Create the Bot
BOT = DOCXAgentBot(CONVERSATION_STATE, USER_STATE)

# Catch-all for errors
async def on_error(context, error):
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()

    # Send a message to the user
    await context.send_activity("The bot encountered an error or bug.")
    await context.send_activity(
        "To continue to run this bot, please fix the bot source code."
    )
    if context.activity.channel_id == "emulator":
        trace_activity = Activity(
            label="TurnError",
            name="on_turn_error Trace",
            timestamp=datetime.utcnow(),
            type=ActivityTypes.trace,
            value=f"{error}",
            value_type="https://www.botframework.com/schemas/error",
        )
        await context.send_activity(trace_activity)


    await CONVERSATION_STATE.delete(context)
    await USER_STATE.delete(context)

ADAPTER.on_turn_error = on_error

async def messages(req: Request) -> Response:
    if "application/json" in req.headers["Content-Type"]:
        body = await req.json()
    else:
        return Response(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

    activity = Activity().deserialize(body)
    auth_header = req.headers["Authorization"] if "Authorization" in req.headers else ""

    response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
    if response:
        return json_response(data=response.body, status=response.status)
    return Response(status=HTTPStatus.OK)

# Health check endpoint
async def health_check(req: Request) -> Response:
    return json_response({"status": "healthy", "service": "docx-agent-teams-bot"})

def init_func(argv):
    APP = web.Application(middlewares=[aiohttp_error_middleware])
    APP.router.add_post("/api/messages", messages)
    APP.router.add_get("/health", health_check)
    return APP

if __name__ == "__main__":
    APP = init_func(None)
    
    try:
        web.run_app(APP, host="0.0.0.0", port=DefaultConfig.PORT)
    except Exception as error:
        raise error
      
