from globals import speechtotext_manager, openai_manager, obswebsockets_manager
from read_text_file import read_file
import threading

BACKUP_FILE = "chat_back.txt"

# add context to OpenAI
somnia = read_file("Somnia.txt")
openai_manager.chat_history.append({"role": "system", "content": somnia})

thread_lock = threading.Lock()


def talk_to_somnia(text, skip_ai=False):
    if not skip_ai:
        # Send question to OpenAi
        text = openai_manager.chat(text)
        with thread_lock:
            # Write the results to txt file as a backup
            with open(BACKUP_FILE, "w") as file:
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
