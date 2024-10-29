import json


def to_msg(
    text: str,
    skip_ai: bool = False,
    sleep_time: int = 5,
    peek=False,
    skip_history=False,
    single_prompt=False,
    gun=False,
) -> str:
    return json.dumps(
        {
            "type": "question",
            "text": text,
            "skip_ai": skip_ai,
            "sleep_time": sleep_time,
            "peek": peek,
            "skip_history": skip_history,
            "single_prompt": single_prompt,
            "gun": gun,
        }
    )


def from_msg(msg: str) -> tuple[str, bool, int, bool, bool, bool, bool] | None:
    match json.loads(msg):
        case {
            "type": "question",
            "text": text,
            "skip_ai": skip_ai,
            "sleep_time": sleep_time,
            "peek": peek,
            "skip_history": skip_history,
            "single_prompt": single_prompt,
            "gun": gun,
        }:
            return text, skip_ai, sleep_time, peek, skip_history, single_prompt, gun

    return None
