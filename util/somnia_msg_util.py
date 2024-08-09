import json


def to_msg(text: str, skip_ai: bool = False, sleep_time: int = 5) -> str:
    return json.dumps(
        {"type": "question", "text": text, "skip_ai": skip_ai, "sleep_time": sleep_time}
    )


# TODO: use match syntax
def from_msg(msg: str) -> tuple[str, bool, int] | None:
    match json.loads(msg):
        case {
            "type": "question",
            "text": text,
            "skip_ai": skip_ai,
            "sleep_time": sleep_time,
        }:
            return text, skip_ai, sleep_time

    return None
