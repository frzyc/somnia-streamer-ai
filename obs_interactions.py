import asyncio
from rich import print
from globals import getOBSWebsocketsManager
from obs_websocket import OBSWebsocketsManager

pngtuber = {
    "sceneName": "pngtuber",
    "bonjour": "bonjour",
    "rainbow": "rainbow",  # a rainbow filter on the "bonjour" source
}
unionbreak = {
    "sceneName": "unionbreak",
    "text": "unionbreak_text",
    "meeting": "Emergency Meeting",
}
mic_in = {"sceneName": "Audio stuff", "srcName": "Mic in"}


class ObsInteractions:

    def __init__(self, obs: OBSWebsocketsManager):
        self.obs = obs

    def bonjour(self):
        print("[green]OBS: Toggling Mustache...")
        visbility = self.obs.get_source_visibility(
            pngtuber["sceneName"], pngtuber["bonjour"]
        )
        self.obs.set_source_visibility(
            pngtuber["sceneName"], pngtuber["bonjour"], not visbility
        )

    def bonjourRainbow(self):
        print("[green]OBS: Toggling MustacheRainbow...")
        visbility = self.obs.get_filter_visibility(
            pngtuber["bonjour"], pngtuber["rainbow"]
        )
        self.obs.set_filter_visibility(
            pngtuber["bonjour"], pngtuber["rainbow"], not visbility
        )

    async def memeFormat(self, text: str):
        print("[green]OBS: Setting meme format...")
        self.obs.set_text("meme text", text)
        self.obs.set_scene("meme format")
        self.obs.set_filter_visibility("Game/Desktop Clone", "Freeze", True)
        await asyncio.sleep(5)
        self.obs.set_scene("Game/Desktop")
        self.obs.set_filter_visibility("Game/Desktop Clone", "Freeze", False)

    async def unionBreak(self, chat, runAds):
        print("[green]OBS: Toggling Union Break...")
        onBreak = self.obs.get_source_visibility(
            unionbreak["sceneName"], unionbreak["text"]
        )
        if not onBreak:
            self.obs.set_source_visibility(
                unionbreak["sceneName"], unionbreak["meeting"], True
            )
            await chat(
                "I'm going on a union break. Don't worry, I will be back soon. If you are bored, play around with some !commands, or ask Somnia a question(point redeem)."
            )
        else:
            await chat("I'm back! Hope you didn't miss me too much...")
        self.obs.set_source_visibility(
            unionbreak["sceneName"], unionbreak["text"], not onBreak
        )
        enString = "Enabled" if onBreak else "Disabled"
        print(f"[green]OBS: Mic in {enString}")
        self.obs.set_source_visibility(mic_in["sceneName"], mic_in["srcName"], onBreak)
        if not onBreak:
            await runAds()
            await asyncio.sleep(1)
            print(f"disble meeting")
            self.obs.set_source_visibility(
                unionbreak["sceneName"], unionbreak["meeting"], False
            )


if __name__ == "__main__":
    # ObsInteractions().bonjour()

    # asyncio.run(ObsInteractions().memeFormat("test"))

    ### Test Union Break
    async def aprint(*args):
        print(*args)

    asyncio.run(ObsInteractions(getOBSWebsocketsManager()).unionBreak(aprint))
