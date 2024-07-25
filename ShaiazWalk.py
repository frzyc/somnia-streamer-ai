import time
from globals import getOBSWebsocketsManager


def shaiazWalk():
    laps = 0
    obswebsockets_manager = getOBSWebsocketsManager()
    # make sure the position alignment is at bottom center
    SOURCE_SCENE_NAME = "Game/Desktop"
    SOURCE_SCENE_FOLDER = "shiazwalk"
    SOURCE_GIF = "shiazwalkgif"
    SOURCE_NAME_LABEL = "shiazwalklabel"
    transform = obswebsockets_manager.get_source_transform(
        SOURCE_SCENE_FOLDER, SOURCE_GIF
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
        if (x <= eleWidth / 2) and dx < 0:
            dx = 1
            laps = laps + 1
        elif (x > (SCREEN_WIDTH - eleWidth / 2)) and dx > 0:
            dx = -1
        x = x + dx * speed * timeRate
        y = y + dy * speed * timeRate
        obswebsockets_manager.set_text(SOURCE_NAME_LABEL, f"Laps: {laps}")
        obswebsockets_manager.set_source_transform(
            SOURCE_SCENE_NAME,
            SOURCE_SCENE_FOLDER,
            {
                "positionX": abs(x),
                "positionY": y,
            },
        )
        obswebsockets_manager.set_source_transform(
            SOURCE_SCENE_FOLDER,
            SOURCE_GIF,
            {
                "scaleX": dx * scalex,
            },
        )


if __name__ == "__main__":
    shaiazWalk()
