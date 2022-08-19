from twitchio.ext import commands
import os
from utils.dbcontrol import Database

class Bot(commands.Bot):
    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        super().__init__(token=os.environ['bot_access_token'], prefix='?', initial_channels=['ayberkenis', 'ayberkenis_bot'])
        self.db = Database()
        self.load_cogs()

    async def event_ready(self):
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')
        await self.db.first_setup()




    def load_cogs(self):
        for file in sorted(os.listdir("twitch_cogs")):
            if file.endswith(".py"):
                self.load_module("twitch_cogs." + file[:-3])
                print(f"[TWITCH] Module `{file[:-3]}` has been loaded successfully")



bot = Bot()
bot.run()
