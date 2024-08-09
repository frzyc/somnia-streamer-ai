import json


def set_multi(multi: float):
    return json.dumps({"type": "set_multi", "multi": multi})


def set_multi_stack(stacks: int):
    return json.dumps({"type": "set_multi_stack", "stacks": stacks})


def add_speed(speed: float):
    return json.dumps({"type": "add_speed", "speed": speed})


def speed_added(speed: float):
    return json.dumps({"type": "speed_added", "speed": speed})


def set_laps(laps: int):
    return json.dumps({"type": "set_laps", "laps": laps})


def get_debug():
    return json.dumps({"type": "get_debug"})


def debug_msg(speed, multi, laps):
    return json.dumps(
        {"type": "debug_msg", "speed": speed, "multi": multi, "laps": laps}
    )


def parse_debug(msg: str):
    data = json.loads(msg)
    match data:
        case {"type": "debug_msg", "speed": speed, "multi": multi, "laps": laps}:
            return speed, multi, laps
