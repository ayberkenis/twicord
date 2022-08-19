from twitchio.ext import commands
from datetime import datetime

class CustomCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def customcommand(self, ctx: commands.Context):
        await ctx.send(f"Timer set, {ctx.author.name}!")

    @commands.Cog.event()
    async def event_message(self, message):
        # An event inside a cog!
        if message.echo:
            return

        try:
            if message.content.startswith('?'):
                data = await self.check_is_a_custom(str(message.content).split(" ")[0])
                if data:
                    if data['name']:
                        if data['last_usage_timestamp'] + data['cooldown'] < int(datetime.utcnow().timestamp()):
                            print(data['last_usage_timestamp'] + data['cooldown'] < int(datetime.utcnow().timestamp()))
                            await self.update_last_usage(data['name'])
                            await message.channel.send(data['response'])
                        else:
                            time_left = data['last_usage_timestamp'] + data['cooldown'] - int(datetime.utcnow().timestamp())
                            await message.channel.send(f'Command is in cooldown for {time_left} seconds.')
        except commands.CommandNotFound:
            pass

    async def check_is_a_custom(self, content):
        data = await self.bot.db.fetch('SELECT * FROM custom_commands WHERE name = ?', [content[1:], ])

        return data

    async def update_last_usage(self, cmd_name):
        await self.bot.db.execute('UPDATE custom_commands SET last_usage_timestamp = ? WHERE name = ?',
                                  [int(datetime.utcnow().timestamp()), cmd_name])

def prepare(bot: commands.Bot):
    # Load our cog with this module...
    bot.add_cog(CustomCommands(bot))