from globals import getAzureSpeechAIManager, getOpenAiManager, getOBSWebsocketsManager
from obs_interactions import ObsInteractions
from util.read_text_file import read_file
import threading
from dotenv import load_dotenv
import time
import asyncio
from websockets.server import serve
import os
from util.somnia_msg_util import from_msg
from websockets import ConnectionClosedOK
import websockets
from rich import print
import random

# Just in case this file is loaded alone
load_dotenv(dotenv_path=".env.local")

BACKUP_FILE = "chat_back.txt"

# add context to OpenAI
somnia = read_file("Somnia.txt")
openai_manager = getOpenAiManager()
speechtotext_manager = getAzureSpeechAIManager()
openai_manager.system_prompt = somnia

obsm = getOBSWebsocketsManager()
obs = ObsInteractions(obsm)

thread_lock = threading.Lock()


def talk_to_somnia(
    text,
    skip_ai=False,
    sleep_time=5,
    peek=False,
    skip_history=False,
    single_prompt=False,
):
    if not skip_ai:
        # Send question to OpenAi
        text = openai_manager.chat(
            text,
            skip_history=skip_history,
            single_prompt=single_prompt,
            override_system=override_system_promot(),
        )
        if not text:
            return
        with thread_lock:
            # Write the results to txt file as a backup
            with open(BACKUP_FILE, "w", encoding="utf-8") as file:
                file.write(str(openai_manager.chat_history))
    with thread_lock:
        hide = obs.showSomnia(text, peek)
        speechtotext_manager.tts(text)
        hide()
        time.sleep(sleep_time)


def override_system_promot() -> str | None:
    if random.random() < 0.1:
        return (
            somnia + '- You have brainrot, use the phrase "very mindful, very demure".'
        )
    return None


async def handle_socket(websocket):
    try:
        async for message in websocket:
            data = from_msg(message)
            if data is None:
                continue
            (text, skip_ai, sleep_time, peek, skip_history, single_prompt) = data
            talk_to_somnia(text, skip_ai, sleep_time, peek, skip_history, single_prompt)
    except ConnectionClosedOK:
        print("Connection closed")
    except websockets.exceptions.ConnectionClosedError:
        print("Connection reset")


SOCKET_PORT_SOMNIA = int(os.getenv("SOCKET_PORT_SOMNIA"))


async def main():
    async with serve(handle_socket, "localhost", SOCKET_PORT_SOMNIA):
        talk_to_somnia("You've been brought online, say a greeting.")
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
