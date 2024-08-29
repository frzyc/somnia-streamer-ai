import time
from openai import OpenAI
from rich import print
from dotenv import load_dotenv

import os
import tiktoken

# Just in case this file is loaded alone
load_dotenv(dotenv_path=".env.local")
TOKEN_LIMT = 8000
WINDOW = 60 * 60  # 1 hour


def num_tokens_from_messages(messages, model="gpt-4o"):
    """Returns the number of tokens used by a list of messages.
    Copied with minor changes from: https://platform.openai.com/docs/guides/chat/managing-tokens
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
        num_tokens = 0
        for message in messages:
            num_tokens += (
                4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
            )
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":  # if there's a name, the role is omitted
                    num_tokens += -1  # role is always required and always 1 token
        num_tokens += 2  # every reply is primed with <im_start>assistant
        return num_tokens
    except Exception:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not presently implemented for model {model}.
        #See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )


class OpenAiManager:
    system_prompt = None

    def __init__(self):
        self.chat_history = []
        try:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        except Exception as e:
            print(e)
            exit("invalid OpenAI key")

    def chat(self, msg, skip_history=False):
        window_cutoff = time.time() - WINDOW
        if not msg:
            return print("[red]Empty message[/red]")

        prompt = {"role": "user", "content": msg, "timestamp": time.time()}
        if not skip_history:
            self.chat_history.append(prompt)

        # Make a msg list for chatgpt with timestamp removed
        msgs = [
            {k: v for (k, v) in msg.items() if k != "timestamp"}
            for msg in self.chat_history
            if msg["timestamp"] > window_cutoff
        ]
        # add system prompt
        if self.system_prompt:
            msgs.insert(0, self.system_prompt)

        tokens = num_tokens_from_messages(msgs)
        print(f"[bold]Token usage: {tokens} tokens...")
        if tokens > TOKEN_LIMT:
            return print(
                "The length of this chat question is too large for the GPT model"
            )

        print("[yellow]Asking ChatGPT...")
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini", messages=msgs
        )

        answer = completion.choices[0].message.content
        print(f"[green]\n{answer}\n")
        return answer


# testing stuff
if __name__ == "__main__":
    openai_manager = OpenAiManager()

    openai_manager.system_prompt = {
        "role": "system",
        "content": "Act like you are drunk but are trying to pass off that you are completely sober ",
    }

    while True:
        new_prompt = input("Ask me something?")
        openai_manager.chat(new_prompt)
