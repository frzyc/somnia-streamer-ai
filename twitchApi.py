import asyncio
from typing import Any
import websockets
import json
import os
from dotenv import load_dotenv
from websockets.exceptions import ConnectionClosedError
from rich import print
import aiohttp
from globals import getOBSWebsocketsManager

load_dotenv(dotenv_path=".env.local")
TWITCH_OWNER_ID = os.getenv("TWITCH_OWNER_ID")
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
TWITCH_ACCESS_TOKEN = os.getenv("TWITCH_ACCESS_TOKEN")
obswebsockets_manager = getOBSWebsocketsManager()

# A simple API to deal with whatever twitchio couldn't handle (mainly ad break)


async def connect_to_twitch():
    uri = "wss://eventsub.wss.twitch.tv/ws"

    try:
        async with websockets.connect(
            uri,
            extra_headers={
                "Client-Id": TWITCH_CLIENT_ID,
                "Authorization": f"Bearer {TWITCH_ACCESS_TOKEN}",
            },
        ) as websocket:
            await handle_events(websocket)
    except ConnectionClosedError as e:
        print("[red]Connection closed.", e)


async def subscribe_to_events(payload: dict[str, Any]):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.twitch.tv/helix/eventsub/subscriptions",
            headers={
                "Client-Id": TWITCH_CLIENT_ID,
                "Authorization": f"Bearer {TWITCH_ACCESS_TOKEN}",
            },
            json=payload,
        ) as response:
            response_json = await response.json()
            print(response_json)


def update_payload(twitch_session_id: str):
    return {
        "type": "user.update",
        "version": "1",
        "condition": {"user_id": TWITCH_OWNER_ID},
        "transport": {
            "method": "websocket",
            "session_id": twitch_session_id,
        },
    }


def ad_break_payload(twitch_session_id: str):
    return {
        "type": "channel.ad_break.begin",
        "version": "1",
        "condition": {"broadcaster_user_id": TWITCH_OWNER_ID},
        "transport": {
            "method": "websocket",
            "session_id": twitch_session_id,
        },
    }


async def handle_events(websocket):
    print("[green]Handling events...")
    async for message in websocket:
        event = json.loads(message)
        msg_type = event["metadata"]["message_type"]
        if msg_type == "session_keepalive":
            continue
        print("[yellow]Event received:", event)
        # Add your event handling logic here
        if msg_type == "session_welcome":
            twitch_session_id = event["payload"]["session"]["id"]
            await subscribe_to_events(update_payload(twitch_session_id))
            await subscribe_to_events(ad_break_payload(twitch_session_id))
            continue
        elif msg_type == "notification":
            # Handling subscriptions
            if "subscription" in event["payload"]:
                if event["payload"]["subscription"]["type"] == "channel.ad_break.begin":
                    print("[yellow]Ad break started")
                    obswebsockets_manager.set_source_visibility(
                        "Game/Desktop", "Bezos Time", True
                    )
                    obswebsockets_manager.set_source_visibility(
                        "Game/Desktop", "Bezos", True
                    )
                    await asyncio.sleep(0.5)
                    obswebsockets_manager.set_source_visibility(
                        "Game/Desktop", "shaiaz", True
                    )
                    duration = event["payload"]["event"]["duration_seconds"]
                    await asyncio.sleep(duration)
                    obswebsockets_manager.set_source_visibility(
                        "Game/Desktop", "shaiaz", False
                    )
                    await asyncio.sleep(0.5)
                    obswebsockets_manager.set_source_visibility(
                        "Game/Desktop", "Bezos Time", False
                    )
                    obswebsockets_manager.set_source_visibility(
                        "Game/Desktop", "Bezos", False
                    )

                    print("[yellow]Ad break over")
        elif msg_type == "notification":
            print("[red]TODO: need to handle reconnect")
    print("[red]Finished handling events?")


if __name__ == "__main__":
    asyncio.run(connect_to_twitch())
