from dotenv import load_dotenv
import keyboard
from keyboard import call_later
from rich import print
from somnia import talk_to_somnia
from globals import speechtotext_manager
from dotenv import load_dotenv
import os
from websockets.sync.client import connect
import json
from util.somnia_msg_util import to_msg

# Just in case this file is loaded alone
load_dotenv(dotenv_path=".env.local")

SOCKET_PORT_SOMNIA = os.getenv("SOCKET_PORT_SOMNIA")
websocket = connect(f"ws://localhost:{SOCKET_PORT_SOMNIA}")


def mic_handler():
    print("[green]Now listening to your microphone:")
    mic_result = speechtotext_manager.stt_from_mic()

    if mic_result == "":
        print("[red]Did not receive any input from your microphone!")
        return
    websocket.send(to_msg(mic_result))


def handle_text_input(skip_ai=False):
    text = input(f"[bold]Enter a question{'(skip ai)' if skip_ai else ''}:")
    if not text:
        return

    websocket.send(to_msg(text, skip_ai))


def main():
    keyboard.add_hotkey("f4", lambda: call_later(mic_handler))
    keyboard.add_hotkey("ctrl+shift+f4", lambda: call_later(handle_text_input))
    keyboard.add_hotkey(
        "ctrl+shift+alt+f4", lambda: call_later(handle_text_input, args=(True,))
    )

    print("[green]press F4 to talk via your microphone")
    print("[green]press ctrl+shift+F4 to enter text directly")
    print("[green]press shift+esc to exit")
    keyboard.wait("shift+esc")


if __name__ == "__main__":
    main()
