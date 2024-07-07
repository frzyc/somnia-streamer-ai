from globals import getAzureSpeechAIManager, getOpenAiManager, getOBSWebsocketsManager
from util.read_text_file import read_file
import threading
from dotenv import load_dotenv
import time
import asyncio
from websockets.server import serve
import os
from util.msgUtil import fromMsg
from websockets import ConnectionClosedOK
import websockets

# Just in case this file is loaded alone
load_dotenv(dotenv_path=".env.local")

BACKUP_FILE = "chat_back.txt"

# add context to OpenAI
somnia = read_file("Somnia.txt")
openai_manager = getOpenAiManager()
obswebsockets_manager = getOBSWebsocketsManager()
speechtotext_manager = getAzureSpeechAIManager()
openai_manager.chat_history.append({"role": "system", "content": somnia})

thread_lock = threading.Lock()


def talk_to_somnia(text, skip_ai=False, sleep_time=5):
    if not skip_ai:
        # Send question to OpenAi
        text = openai_manager.chat(text)
        with thread_lock:
            # Write the results to txt file as a backup
            with open(BACKUP_FILE, "w", encoding="utf-8") as file:
                file.write(str(openai_manager.chat_history))
    with thread_lock:
        obswebsockets_manager.set_source_visibility("Game/Desktop", "somnia", True)
        obswebsockets_manager.set_text("somnia says", text)
        obswebsockets_manager.set_source_visibility("Game/Desktop", "somnia says", True)
        speechtotext_manager.tts(text)
        obswebsockets_manager.set_source_visibility("Game/Desktop", "somnia", False)
        obswebsockets_manager.set_source_visibility(
            "Game/Desktop", "somnia says", False
        )
        time.sleep(sleep_time)


async def handle_socket(websocket):
    try:
        async for message in websocket:
            data = fromMsg(message)
            if data is None:
                continue
            [text, skip_ai, sleep_time] = data
            talk_to_somnia(text, skip_ai, sleep_time)
    except ConnectionClosedOK:
        print("Connection closed")
    except websockets.exceptions.ConnectionClosedError:
        print("Connection reset")


SOCKET_PORT_SOMNIA = int(os.getenv("SOCKET_PORT_SOMNIA"))


async def main():
    async with serve(handle_socket, "localhost", SOCKET_PORT_SOMNIA):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
