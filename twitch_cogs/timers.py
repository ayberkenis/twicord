from twitchio.ext import commands, routines

class Timers(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def timer_set(self, ctx: commands.Context):
        await ctx.send(f"Timer set, {ctx.author.name}!")

    @commands.Cog.event()
    async def event_message(self, message):
        # An event inside a cog!
        if message.echo:
            return

    @routines.routine(minutes=5)
    async def timer_handler(self, seconds=None):
        print('Timer handler')

def prepare(bot: commands.Bot):
    # Load our cog with this module...
    bot.add_cog(Timers(bot))