import json


def to_msg(
    text: str,
    skip_ai: bool = False,
    sleep_time: int = 5,
    peek=False,
    skip_history=False,
) -> str:
    return json.dumps(
        {
            "type": "question",
            "text": text,
            "skip_ai": skip_ai,
            "sleep_time": sleep_time,
            "peek": peek,
            "skip_history": skip_history,
        }
    )


def from_msg(msg: str) -> tuple[str, bool, int] | None:
    match json.loads(msg):
        case {
            "type": "question",
            "text": text,
            "skip_ai": skip_ai,
            "sleep_time": sleep_time,
            "peek": peek,
            "skip_history": skip_history,
        }:
            return text, skip_ai, sleep_time, peek, skip_history

    return None
