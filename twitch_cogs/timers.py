from twitchio.ext import commands, routines
import asyncio
from datetime import datetime
import time
import twitchio


class Timer:
    def __init__(self, data):
        self.data = data
        for key in self.data.keys():
            setattr(self, key, self.data[key])

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def __str__(self):
        return self.response

    def __repr__(self):
        return f"<Twicord Timer [ID: {self.id}]>"


class Timers(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.all_timers = None
        self.timestamp = None
        self.messages_sent = {}

    async def create_task(self, func:callable, *args, **kwargs):
        return await asyncio.create_task(func(*args, **kwargs))

    def dict_from_row(self, row):
        lists_of_dicts = []
        for i in row:
            lists_of_dicts.append(Timer(i))
        return lists_of_dicts

    async def cache_timers(self):
        self.all_timers = await self.bot.db.fetch('SELECT * FROM timers')
        self.all_timers = self.dict_from_row(self.all_timers)
        return self.all_timers

    async def function_worker(self):
        await self.bot.wait_for_ready()
        count = 0
        start = time.time()
        while True:
            current_timestamp = int(datetime.utcnow().timestamp())
            for i, timer in enumerate(self.all_timers):
                if 'last_used' in timer.__dir__() and timer['last_used'] + timer.interval > current_timestamp:
                    continue

                timer['last_used'] = current_timestamp
                self.all_timers[i] = timer
                channel = self.bot.get_channel(timer.channel)
                end = time.time()
                count += 1
                await channel.send(f"Count: {count} | Time:{round(end-start, 2)} | {timer['response']}")
            await asyncio.sleep(2.5)


    async def cache_message_count(self, channel: twitchio.Channel):
        if channel.name not in self.messages_sent.keys():
            self.messages_sent[channel.name] = 0
        else:
            self.messages_sent[channel.name] += 1


    async def refresh_timer_cache(self):
        await self.cache_timers()
        self.timestamp = int(datetime.utcnow().timestamp())
        return self.all_timers

    @commands.Cog.event()
    async def event_message(self, message):
        if message.echo:
            return

        await self.cache_message_count(message.channel)



    @commands.Cog.event()
    async def event_ready(self):
        await self.create_task(self.cache_timers)
        await self.create_task(self.function_worker)


    @commands.command()
    async def add_timer(self, ctx: commands.Context, name, interval, min_chat, is_also_command, *, response):
        await self.bot.db.execute('INSERT INTO timers (name, interval, min_chat, is_also_command, response) VALUES (?, ?, ?, ?, ?)',
                                  [name, interval, min_chat, is_also_command, response])
        await ctx.send(f'Timer {name} has been added.')

    @commands.command()
    async def refresh_timers(self, ctx):
        await self.refresh_timer_cache()
        await ctx.send(f'Timers have been refreshed.')

def prepare(bot: commands.Bot):
    bot.add_cog(Timers(bot))