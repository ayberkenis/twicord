from twitchio.ext import commands
import os
from utils.dbcontrol import Database
import asyncio
from ws import WebServer
import os

ws = WebServer()

class Bot(commands.Bot):

    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        super().__init__(token=os.environ['bot_access_token'], prefix='?', initial_channels=['ayberkenis'])

    async def __ainit__(self):
        await ws.run()

    async def event_ready(self):
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')
        await self.load_cogs()
        await Database().first_setup(self.nick, os.environ['bot_client_id'])



    async def load_cogs(self):
        for file in sorted(os.listdir("twitch_cogs")):
            if file.endswith(".py"):
                self.load_module("twitch_cogs." + file[:-3])
                print(f"Module `{file[:-3]}` has been loaded successfully")

    @commands.command()
    async def hello(self, ctx: commands.Context):
        # Send a hello back!
        await ctx.send(f'Hello {ctx.author.name}!')



bot = Bot()
bot.loop.run_until_complete(bot.__ainit__())
bot.run()
