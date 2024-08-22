import threading
import time
from globals import getOBSWebsocketsManager
from obs_websocket import OBSWebsocketsManager
from util.number import clamp
import asyncio
from rich import print
from websockets.server import serve
from websockets import ConnectionClosedOK
import websockets
import os
import json
from util.streampet_msg_util import *

SCREEN_WIDTH = 1920 * 2
SCREEN_HEIGHT = 1080 * 2
# make sure the position alignment is at bottom center
SOURCE_SCENE_NAME = "HUD"
SOURCE_SCENE_GROUP = "streampet"
SOURCE_GIF = "ellengif"
SOURCE_GIF_FILTER_RAINBOW = "rainbow"
SOURCE_NAME_LABEL = "streampetlabel"
TIME_RATE = 0.005
MAX_SPEED = 3000
SPEED_DECAY = 25
STACK_MULTI = 0.1
pet_run_event = threading.Event()
pet_run_event.set()


# A smal animated gif that walks from left to right, then back to left. Counts laps, and displays the current lap count.
# Will get slower and slower as it moves. Will require additions of energy via `addSpeed`
class StreamPet:
    def __init__(self, obs: OBSWebsocketsManager):
        self.obs = obs
        self.laps = 0

        transform = obs.get_source_transform(SOURCE_SCENE_GROUP, SOURCE_GIF)
        self.eleWidth = transform["width"]
        self.scalex = abs(transform["scaleX"])

        self.x = self.eleWidth
        self.y = SCREEN_HEIGHT
        self.dx = 1
        self.speed = 1  # initial speed to run it once
        self.runner = None
        self.multi = 1  # energy multiplier
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.run_runner()

    def set_laps(self, laps):
        self.laps = laps

    def set_multi_stack(self, stacks):
        self.set_multi(1 + stacks * STACK_MULTI)

    def set_multi(self, multi):
        self.multi = multi

    def add_speed(self, speed):
        moar_speed = speed * self.multi
        self.speed = self.speed + moar_speed
        self.run_runner()
        return moar_speed

    def run_runner(self):
        if self.runner is not None:
            return
        self.runner = self.loop.create_task(self.run())
        self.runner.add_done_callback(self.runner_done)

    def check_disappear(self):
        if self.speed <= 0:
            self.obs.set_source_visibility(SOURCE_SCENE_NAME, SOURCE_SCENE_GROUP, False)

    async def run(self):
        self.obs.set_source_visibility(SOURCE_SCENE_NAME, SOURCE_SCENE_GROUP, True)
        while pet_run_event.is_set():
            if self.speed > 0:
                self.move()
                self.add_speed(-(SPEED_DECAY * TIME_RATE))
            time.sleep(TIME_RATE)
        self.loop.stop()

    def move(self):
        if (self.x <= self.eleWidth / 2) and self.dx < 0:
            self.dx = 1
            self.laps = self.laps + 1
        elif (self.x > (SCREEN_WIDTH - self.eleWidth / 2)) and self.dx > 0:
            self.dx = -1
        self.x = self.x + self.dx * clamp(self.speed, 0, MAX_SPEED) * TIME_RATE
        if self.multi > 1.5:
            self.obs.set_text(
                SOURCE_NAME_LABEL,
                f"Laps: {self.laps} (x{self.multi:.1f})",
            )
        else:
            self.obs.set_text(SOURCE_NAME_LABEL, f"Laps: {self.laps}")
        self.obs.set_source_transform(
            SOURCE_SCENE_NAME,
            SOURCE_SCENE_GROUP,
            {
                "positionX": self.x,
                "positionY": self.y,
            },
        )
        # self.obs.set_source_transform(
        #     SOURCE_SCENE_GROUP,
        #     SOURCE_GIF,
        #     {
        #         "scaleX": self.dx * self.scalex,
        #     },
        # )
        self.obs.set_filter_visibility(
            SOURCE_GIF,
            SOURCE_GIF_FILTER_RAINBOW,
            self.speed > (MAX_SPEED * 0.7),
        )

    def runner_done(self, task):
        self.runner = None


def handle_pet():
    global stream_pet
    stream_pet = StreamPet(getOBSWebsocketsManager())
    stream_pet.loop.run_until_complete(stream_pet.runner)
    stream_pet.loop.run_forever()
    print("[red]Pet is deadged...[/red]")


async def handle_socket(websocket):
    global stream_pet
    try:
        async for message in websocket:
            data = json.loads(message)
            if data is None:
                continue
            match data:
                case {"type": "set_laps", "laps": laps}:
                    stream_pet.set_laps(laps)
                case {"type": "set_multi", "multi": multi}:
                    stream_pet.set_multi(multi)
                case {"type": "set_multi_stack", "stacks": stacks}:
                    stream_pet.set_multi_stack(stacks)
                case {"type": "add_speed", "speed": speed}:
                    speed_moar = stream_pet.add_speed(speed)
                    await websocket.send(speed_added(speed_moar))
                case {"type": "get_debug"}:
                    await websocket.send(
                        debug_msg(stream_pet.speed, stream_pet.multi, stream_pet.laps)
                    )

    except ConnectionClosedOK:
        print("Connection closed")
    except websockets.exceptions.ConnectionClosedError:
        print("Connection reset")


SOCKET_STREAM_PET = int(os.getenv("SOCKET_STREAM_PET"))


async def main():
    async with serve(handle_socket, "localhost", SOCKET_STREAM_PET):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    petthread = threading.Thread(target=handle_pet)
    petthread.start()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[red]Keyboard interrupt...[/red]")

    print("[yellow]Stopping pet...[/yellow]")
    pet_run_event.clear()
    petthread.join()
