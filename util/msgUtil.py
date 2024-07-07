import json


def toMsg(text: str, skip_ai: bool = False, sleep_time: int = 5) -> str:
    return json.dumps(
        {"type": "question", "text": text, "skip_ai": skip_ai, "sleep_time": sleep_time}
    )


def fromMsg(msg: str) -> list | None:
    data = json.loads(msg)
    if data.get("type", "") == "question":
        text = data.get("text", "")
        skip_ai = data.get("skip_ai", False)
        sleep_time = data.get("sleep_time", 5)
        return [text, skip_ai, sleep_time]
    return None
