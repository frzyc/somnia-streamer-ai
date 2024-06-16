from openai import OpenAI
from rich import print
from dotenv import load_dotenv

import os
import tiktoken

# Just in case this file is loaded alone
load_dotenv(dotenv_path=".env.local")
TOKEN_LIMT = 8000


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
    def __init__(self):
        self.chat_history = []
        try:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        except Exception as e:
            print(e)
            exit("invalid OpenAI key")

    def chat(self, msg, use_history=True):
        if not msg:
            return print("[red]Empty message[/red]")

        prompt = {"role": "user", "content": msg}
        if use_history:
            self.chat_history.append(prompt)
        tokens = num_tokens_from_messages(
            self.chat_history if use_history else [prompt]
        )
        print(f"[bold]Token usage: {tokens} tokens...")
        if tokens > TOKEN_LIMT:
            return print(
                "The length of this chat question is too large for the GPT model"
            )

        print("[yellow]Asking ChatGPT...")
        completion = self.client.chat.completions.create(
            model="gpt-4", messages=self.chat_history if use_history else [prompt]
        )

        answer = completion.choices[0].message.content
        print(f"[green]\n{answer}\n")
        return answer


# testing stuff
if __name__ == "__main__":
    openai_manager = OpenAiManager()

    chat_without_history = openai_manager.chat(
        "Hellow, please tell me what is the purpose of life. but tell me in pig Latin",
        use_history=False,
    )

    openai_manager.chat_history.append(
        {
            "role": "system",
            "content": "Act like you are drunk but are trying to pass off that you are completely sober ",
        }
    )

    while True:
        new_prompt = input("Ask me something?")
        openai_manager.chat(new_prompt)
