import threading
from twitchio.channel import Channel
from twitchio.ext import commands, eventsub
from dotenv import load_dotenv
import os
from websockets.sync.client import connect
from util.somnia_msg_util import to_msg
from rich import print
import aiohttp
import asyncio
import pygame
from obs_interactions import ObsInteractions
from globals import getOBSWebsocketsManager
import time
import json
from util.streampet_msg_util import (
    set_multi_stack,
    add_speed,
    set_laps,
    get_debug,
    parse_debug,
)

# Just in case this file is loaded alone
load_dotenv(dotenv_path=".env.local")

TWITCH_ACCESS_TOKEN = os.getenv("TWITCH_ACCESS_TOKEN")
TWITCH_REFRESH_TOKEN = os.getenv("TWITCH_REFRESH_TOKEN")
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
TWITCH_OWNER_ID = os.getenv("TWITCH_OWNER_ID")
SOCKET_PORT_SOMNIA = os.getenv("SOCKET_PORT_SOMNIA")
SOCKET_STREAM_PET = os.getenv("SOCKET_STREAM_PET")
obsm = getOBSWebsocketsManager()
obs = ObsInteractions(obsm)
somnia_socket = None
try:
    somnia_socket = connect(f"ws://localhost:{SOCKET_PORT_SOMNIA}")
    print(
        f"[green]Created a websocket connection to Somnia Streamer AI at port:{SOCKET_PORT_SOMNIA}"
    )
except:
    print(
        f"[yellow]Could not connect to Somnia Streamer AI at port:{SOCKET_PORT_SOMNIA}"
    )

streampet_socket = None
try:
    streampet_socket = connect(f"ws://localhost:{SOCKET_STREAM_PET}")
    print(
        f"[green]Created a websocket connection to Stream Pet at port:{SOCKET_STREAM_PET}"
    )
except:
    print(f"[yellow]Could not connect to Stream Pet at port:{SOCKET_STREAM_PET}")


pygame.mixer.init()
pipes = pygame.mixer.Sound("sounds/pipes.mp3")
pipes.set_volume(0.3)  # This sound is loud AF
ping = pygame.mixer.Sound("sounds/ping.mp3")
blind = pygame.mixer.Sound("sounds/im-legally-blind-made-with-Voicemod.mp3")
sus = pygame.mixer.Sound("sounds/Among Us (Role Reveal) - Sound Effect (HD).mp3")
laugh = pygame.mixer.Sound("sounds/sitcom-laughing-1.mp3")
laugh.set_volume(0.3)

MESSAGE_WINDOW_S = 3 * 60


class TwitchBot(commands.Bot):
    messages = []
    tts_username = None

    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        super().__init__(
            token=TWITCH_ACCESS_TOKEN,
            prefix="?",
            initial_channels=["frzyc"],
        )
        self.esclient = eventsub.EventSubWSClient(self)

    async def event_message(self, message):
        # Messages with echo set to True are messages sent by the bot...
        # For now we just want to ignore them...
        if message.echo:
            return
        self.add_message(message.author.name, message.content)
        unique_chatters = list({msg["username"] for msg in self.messages})
        num_unique_chatters = len(unique_chatters)
        if streampet_socket:
            streampet_socket.send(set_multi_stack(num_unique_chatters))
            streampet_socket.send(add_speed(100))
            streampet_socket.recv()

        # Print the contents of our message to console...
        # print(message.content)

        if message.author.name == self.tts_username:
            exclude = (
                message.content.startswith("!")
                or message.content.startswith("?")
                or message.content.startswith("http")
            )
            if not exclude:
                somnia_socket.send(to_msg(message.content, True, 0.5))

        # Since we have commands and are overriding the default `event_message`
        # We must let the bot know we want to handle and invoke our commands...
        await self.handle_commands(message)

    def add_message(self, username, message):
        current_time = int(time.time())
        self.messages = [
            msg
            for msg in self.messages
            if current_time - msg["timestamp"] <= MESSAGE_WINDOW_S
        ]
        self.messages.append(
            {"username": username, "message": message, "timestamp": current_time}
        )

    async def event_ready(self):
        # We are logged in and ready to chat and use commands...
        print(f"Logged in as | {self.nick}")
        print(f"User id is | {self.user_id}")

    async def event_channel_joined(self, channel: Channel):
        print(f"Joined {channel.name}")

    # Eventsubs

    async def sub(self):
        print("Subscribing to EventSubs...")
        await self.esclient.subscribe_channel_stream_start(
            broadcaster=TWITCH_OWNER_ID, token=TWITCH_ACCESS_TOKEN
        )
        await self.esclient.subscribe_channel_stream_end(
            broadcaster=TWITCH_OWNER_ID, token=TWITCH_ACCESS_TOKEN
        )
        await self.esclient.subscribe_channel_points_redeemed(
            broadcaster=TWITCH_OWNER_ID, token=TWITCH_ACCESS_TOKEN
        )
        await self.esclient.subscribe_channel_follows_v2(
            broadcaster=TWITCH_OWNER_ID,
            token=TWITCH_ACCESS_TOKEN,
            moderator=TWITCH_OWNER_ID,
        )
        await self.esclient.subscribe_channel_raid(
            to_broadcaster=TWITCH_OWNER_ID, token=TWITCH_ACCESS_TOKEN
        )
        await self.esclient.subscribe_channel_cheers(
            broadcaster=TWITCH_OWNER_ID, token=TWITCH_ACCESS_TOKEN
        )
        await self.esclient.subscribe_channel_shoutout_receive(
            broadcaster=TWITCH_OWNER_ID,
            token=TWITCH_ACCESS_TOKEN,
            moderator=TWITCH_OWNER_ID,
        )
        await self.esclient.subscribe_channel_subscriptions(
            broadcaster=TWITCH_OWNER_ID, token=TWITCH_ACCESS_TOKEN
        )
        await self.esclient.subscribe_channel_subscription_messages(
            broadcaster=TWITCH_OWNER_ID, token=TWITCH_ACCESS_TOKEN
        )

    async def event_eventsub_notification_channel_reward_redeem(self, payload) -> None:
        data: eventsub.CustomRewardRedemptionAddUpdateData = payload.data
        match data.reward.title:
            case "Ask Somnia a question":
                self.ask_somnia(data.user.name, data.input)
            case "PIPES":
                print("playing pipes")
                pipes.play()
            case "ping":
                print("playing ping")
                ping.play()
            case "blind":
                print("playing blind")
                blind.play()
            case "amogus sus":
                print("playing sus")
                sus.play()
            case "meme format":
                print("playing meme format")
                await obs.memeFormat(data.input)
            case "laugh":
                print("playing laugh")
                laugh.play()
            case "energy drink":
                if streampet_socket:
                    streampet_socket.send(add_speed(1000))
                    msg = streampet_socket.recv()
                    match json.loads(msg):
                        case {"type": "speed_added", "speed": speed_added}:
                            await data.broadcaster.channel.send(
                                f"Giving Ellen an energy drink: {speed_added:.1f} Energy added."
                            )
            case "Australia":
                await obs.australia(data.broadcaster.channel.send, 60)
            case _:
                print(f"unknown redeem: {data.reward.title}")

    async def event_eventsub_notification_stream_start(
        self, payload: eventsub.StreamOnlineData
    ) -> None:
        print("stream started!")
        print(payload)

    async def event_eventsub_notification_stream_end(
        self, payload: eventsub.StreamOnlineData
    ) -> None:
        print("stream ended!")
        print(payload)

    async def event_eventsub_notification_followV2(self, payload) -> None:
        data: eventsub.ChannelFollowData = payload.data
        print(f"{data.user.name} followed woohoo!")
        if streampet_socket:
            streampet_socket.send(add_speed(2000))
            streampet_socket.recv()
        self.somnia_tts_and_respond(
            f"{data.user.name} just followed the channel",
            f"{data.user.name} just followed the channel, please thank them.",
        )

    async def event_eventsub_notification_subscription(self, payload) -> None:
        data: eventsub.ChannelSubscribeData = payload.data
        username = data.user.name if data.user else "Someone"
        print(f"{username} subscribed({data.tier}) woohoo!")
        if streampet_socket:
            streampet_socket.send(add_speed(5000))
            streampet_socket.recv()
        self.somnia_tts_and_respond(
            f"{username} just subscribed to the channel",
            f"{username} just subscribed to the channel, please thank them.",
        )

    async def event_eventsub_notification_subscription_message(self, payload) -> None:
        data: eventsub.ChannelSubscriptionMessageData = payload.data
        username = data.user.name if data.user else "Someone"
        print(f"{username} subscribed({data.tier}) woohoo!")
        if streampet_socket:
            streampet_socket.send(add_speed(5000))
            streampet_socket.recv()
        streak = data.streak
        message = data.message
        self.somnia_tts_and_respond(
            f"{username} subscribed to the channel for {streak} months, with the messaage: {message}",
            f"{username} subscribed to the channel for {streak} months, with the messaage: {message}. please thank them.",
        )

    async def event_eventsub_notification_channel_update(
        self, payload: eventsub.ChannelUpdateData
    ) -> None:
        print("Received event!")
        print(payload)

    async def event_eventsub_notification_raid(self, payload) -> None:
        data: eventsub.ChannelRaidData = payload.data
        raider = data.raider

        print(f"Raid from: {raider.name} ({raider.id})")
        print(f"Viewers count: {data.viewer_count}")
        self.somnia_tts_and_respond(
            f"{raider.name} just raided the channel with {data.viewer_count} viewers.",
            f"{raider.name} just raided the channel with {data.viewer_count} viewers., please thank them.",
        )

    async def event_eventsub_notification_channel_shoutout_receive(
        self, payload
    ) -> None:
        data: eventsub.ChannelShoutoutReceiveData = payload.data
        from_broadcaster = data.from_broadcaster
        print(f"Shoutout from: {from_broadcaster.name} ({from_broadcaster.id})")
        print(f"Viewers count: {data.viewer_count}")
        self.somnia_tts_and_respond(
            f"{from_broadcaster.name} just shoutout the channel with {data.viewer_count} viewers.",
            f"{from_broadcaster.name} just shoutout the channel with {data.viewer_count} viewers, please thank them.",
        )

    # Error handling

    async def event_command_error(
        self, context: commands.Context, error: Exception
    ) -> None:
        if isinstance(error, commands.CommandOnCooldown):
            await context.send(
                f"Wait a couple of seconds before sending something else {context.author.name}!"
            )

    async def event_token_expired(self):
        global TWITCH_ACCESS_TOKEN
        print("[yellow]Token expired, refreshing...")
        TWITCH_ACCESS_TOKEN = await refresh_token()
        return TWITCH_ACCESS_TOKEN

    # Commands
    @commands.command()
    async def hello(self, ctx: commands.Context):
        # Send a hello back!
        await ctx.send(f"Hello {ctx.author.name}!")

    @commands.command()
    async def pipes(self, ctx: commands.Context):
        if ctx.author.id != TWITCH_OWNER_ID:
            return await ctx.send("Sorry, you are not allowed to use this directly.")
        pipes.play()

    @commands.command()
    async def ping(self, ctx: commands.Context):
        if ctx.author.id != TWITCH_OWNER_ID and not ctx.author.is_mod:
            return await ctx.send("Sorry, you are not allowed to use this directly.")
        ping.play()

    @commands.command()
    async def laugh(self, ctx: commands.Context):
        if ctx.author.id != TWITCH_OWNER_ID and not ctx.author.is_mod:
            return await ctx.send("Sorry, you are not allowed to use this directly.")
        laugh.play()

    @commands.command()
    async def blind(self, ctx: commands.Context):
        if ctx.author.id != TWITCH_OWNER_ID and not ctx.author.is_mod:
            return await ctx.send("Sorry, you are not allowed to use this directly.")
        blind.play()

    @commands.command()
    async def bonjour(self, ctx: commands.Context):
        if ctx.author.id != TWITCH_OWNER_ID and not ctx.author.is_mod:
            return await ctx.send("Sorry, you are not allowed to use this directly.")
        await ctx.send("Toggling Mustache...")
        obs.bonjour()

    @commands.command()
    async def bonjourRainbow(self, ctx: commands.Context):
        if ctx.author.id != TWITCH_OWNER_ID and not ctx.author.is_mod:
            return await ctx.send("Sorry, you are not allowed to use this directly.")
        await ctx.send("Toggling Mustache rainbow")
        obs.bonjourRainbow()

    @commands.command(name="unionbreak", aliases=["brb"])
    async def unionbreak(self, ctx: commands.Context):
        if ctx.author.id != TWITCH_OWNER_ID and not ctx.author.is_mod:
            return await ctx.send("Sorry, you are not allowed to use this directly.")

        async def runAds():
            print("Running ads")
            user = await ctx.message.channel.user()
            await user.start_commercial(TWITCH_ACCESS_TOKEN, 180)

        await obs.unionBreak(ctx.send, runAds)

    @commands.command()
    async def laps(self, ctx: commands.Context, laps: int):
        if ctx.author.id != TWITCH_OWNER_ID and not ctx.author.is_mod:
            return await ctx.send("Sorry, you are not allowed to use this directly.")
        if streampet_socket:
            streampet_socket.send(set_laps(int(laps)))

    @commands.command()
    @commands.cooldown(1, 45, commands.Bucket.user)
    # FIXME: does not parse a whole sentence, just the first parameter
    async def somnia(self, ctx: commands.Context, question: str):
        if ctx.author.id != TWITCH_OWNER_ID:
            return await ctx.send("Sorry, you are not allowed to use somnia directly.")
        self.ask_somnia(ctx.author.name, question)

    @commands.command()
    async def tts(self, ctx: commands.Context, username: str):
        if ctx.author.id != TWITCH_OWNER_ID and not ctx.author.is_mod:
            return await ctx.send("Sorry, you are not allowed to use this directly.")
        if username:
            self.tts_username = username.lower()
            return await ctx.send(f"Setting {username} for somnia tts")
        else:
            self.tts_username = None
            return await ctx.send(f"Clearing somnia tts")

    # Helper functions
    def ask_somnia(self, name: str, question: str):
        print(f"[blue]{name} asks Somnia: {question}[/blue]")
        self.somnia_tts_and_respond(f"{name} Ask the question: {question}", question)

    @commands.command()
    async def debug(self, ctx: commands.Context):
        if ctx.author.id != TWITCH_OWNER_ID and not ctx.author.is_mod:
            return await ctx.send("Sorry, you are not allowed to use this directly.")
        if not streampet_socket:
            return
        streampet_socket.send(get_debug())
        msg = streampet_socket.recv()
        data = parse_debug(msg)
        (speed, multi, laps) = data
        await ctx.send(f"Stream pet energy:{speed:.0f} multi:{multi:.2f} laps:{laps}")

    @commands.command()
    async def australia(self, ctx: commands.Context):
        if ctx.author.id != TWITCH_OWNER_ID and not ctx.author.is_mod:
            return await ctx.send("Sorry, you are not allowed to use this directly.")

        await obs.australia(ctx.send, 60)

    @commands.command()
    async def australia_reset(self, ctx: commands.Context):
        if ctx.author.id != TWITCH_OWNER_ID and not ctx.author.is_mod:
            return await ctx.send("Sorry, you are not allowed to use this directly.")
        await obs.reset_webcam_rotation()

    def somnia_tts_and_respond(self, tts: str, prompt: str):
        if not somnia_socket:
            return
        somnia_socket.send(
            to_msg(
                tts,
                skip_ai=True,
            )
        )
        somnia_socket.send(to_msg(prompt))


async def refresh_token():
    params = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": TWITCH_REFRESH_TOKEN,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://id.twitch.tv/oauth2/token", params=params
        ) as response:
            response_json = await response.json()
            access_token = response_json.get("access_token")
            return access_token


def write_env(key: str, value: str):
    if not value:
        raise Exception("value cannot be empty")
    with open(".env.local", "r") as file:
        lines = file.readlines()
        at_line = None
        for line_number, line in enumerate(lines):
            if key in line:
                # Print the line number if the phrase is found
                print(f"{key} found on line {line_number}")
                at_line = line_number
                break  # Exit the loop once the phrase is found
        if at_line == None:
            raise Exception(f"cannot find key({key}) in .env.local")
        lines[line_number] = f"{key}={value}\n"
        with open(".env.local", "w") as wf:
            wf.writelines(lines)


async def refresh_token_and_save():
    global TWITCH_ACCESS_TOKEN
    TWITCH_ACCESS_TOKEN = await refresh_token()
    write_env("TWITCH_ACCESS_TOKEN", TWITCH_ACCESS_TOKEN)
    print("[green]Token refreshed![/green]")


async def refresh_token_and_run(bot: TwitchBot):
    await refresh_token_and_save()
    bot.loop.create_task(bot.sub())
    bot.run()


if __name__ == "__main__":
    try:
        # # originally wanted to catch twitchio.errors.AuthenticationError, then bot.close(), and restart, but that didn't work...
        # # now we refresh the token before running the bot every time.
        asyncio.run(refresh_token_and_save())
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        bot = TwitchBot()
        bot.loop.create_task(bot.sub())
        bot.run()
    except KeyboardInterrupt:
        print("[red]Keyboard interrupt...[/red]")

        pass
    print("[red]Bot is deadged...[/red]")
    asyncio.run(bot.close())
