import time
from globals import getOBSWebsocketsManager
import pygame


def shaiazWalk():
    obswebsockets_manager = getOBSWebsocketsManager()
    # make sure the position alignment is at bottom center
    SOURCE_SCENE_NAME = "Conditional Overlay Stuff"
    SOURCE_NAME = "shiazwalk"
    transform = obswebsockets_manager.get_source_transform(
        SOURCE_SCENE_NAME, SOURCE_NAME
    )
    eleWidth = transform["width"]
    scalex = abs(transform["scaleX"])
    SCREEN_WIDTH = 1920 * 2
    SCREEN_HEIGHT = 1080 * 2
    x = 0
    y = SCREEN_HEIGHT
    dx = 1
    dy = 0
    speed = 1000  # pixels per second
    timeRate = 0.001
    while True:
        time.sleep(timeRate)
        if x <= eleWidth:
            dx = 1
        elif x > (SCREEN_WIDTH - eleWidth):
            dx = -1
        x = x + dx * speed * timeRate
        y = y + dy * speed * timeRate

        obswebsockets_manager.set_source_transform(
            SOURCE_SCENE_NAME,
            SOURCE_NAME,
            {
                "positionX": abs(x),
                "positionY": y,
                "scaleX": dx * scalex,
            },
        )


if __name__ == "__main__":
    shaiazWalk()
