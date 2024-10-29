from twitchio.ext import commands, eventsub, routines
from rich import print
from datetime import datetime
from websockets.sync.client import ClientConnection
from util.somnia_msg_util import to_msg

WORKOUT_COOLDOWN_S = 30 * 60  # 30 minutes


class WorkoutCog(commands.Cog):
    counter = 0

    def __init__(self, bot: commands.Bot, somnia_socket: ClientConnection | None):
        self.somnia_socket = somnia_socket
        self.bot = bot

    @commands.command()
    async def workout_debug(self, ctx: commands.Context):
        await ctx.send(f"Fred has been prompted to workout {self.counter} times.")

    @routines.routine(seconds=WORKOUT_COOLDOWN_S, wait_first=True)
    async def workout_routine(self):
        print("reminder to exercise:", datetime.now().strftime("%H:%M"))
        self.workout_prompt()

    def workout_prompt(self):
        self.counter += 1
        if self.somnia_socket:
            self.somnia_socket.send(
                to_msg(
                    "Its been awhile since Fred last exercised, remind Fred to workout and that he has gotten fat.",
                    peek=True,
                    skip_history=True,
                    single_prompt=True,
                )
            )

    def workout_redeemed(self):
        self.workout_prompt()
        self.workout_routine.restart()

    def enable(self):
        self.workout_routine.start()
        if self.somnia_socket:
            self.somnia_socket.send(
                to_msg(
                    "Workout Module has been enabled.",
                    skip_ai=True,
                )
            )

    def disable(self):
        self.workout_routine.cancel()
        if self.somnia_socket:
            self.somnia_socket.send(
                to_msg(
                    "Workout Module has been disabled.",
                    skip_ai=True,
                )
            )
