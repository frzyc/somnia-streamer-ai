import time
from globals import getOBSWebsocketsManager
import pygame

pygame.mixer.init()
cornersound = pygame.mixer.Sound("sounds/Corner.mp3")


def dvdLogo():
    obswebsockets_manager = getOBSWebsocketsManager()
    SOURCE_SCENE_NAME = "Game/Desktop"
    SOURCE_NAME = "Webcam stuff"
    transform = obswebsockets_manager.get_source_transform(
        SOURCE_SCENE_NAME, SOURCE_NAME
    )
    eleHeight = transform["height"]
    eleWidth = transform["width"]
    OBS_CANVAS_WIDTH = 1920
    OBS_CANVAS_HEIGHT = 1080
    max_x = OBS_CANVAS_WIDTH - eleWidth
    max_y = OBS_CANVAS_HEIGHT - eleHeight
    x = 0
    y = 0
    dx = 1
    dy = 1
    speed = 1000  # pixels per second
    timeRate = 0.005
    while True:
        obswebsockets_manager.set_source_transform(
            SOURCE_SCENE_NAME,
            SOURCE_NAME,
            {
                "positionX": x,
                "positionY": y,
            },
        )
        time.sleep(timeRate)
        x = x + dx * speed * timeRate
        y = y + dy * speed * timeRate
        changex = False
        changey = False
        if x <= 0:
            dx = 1
            changex = True
        elif x > max_x:
            dx = -1
            changex = True
        if y <= 0:
            dy = 1
            changey = True
        if y > max_y:
            dy = -1
            changey = True
        # if changex and changey:
        #     cornersound.play()


if __name__ == "__main__":
    dvdLogo()
