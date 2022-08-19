from twitchio.ext import commands, routines
import asyncio
from datetime import datetime
import time
import twitchio


class Timer:
    def __init__(self, data):
        """
        data must be a dict from the sqlite3 database.
        :param data:
        """
        self.data = data
        self.id = self.data['id']
        self.name = self.data['name']
        self.response = self.data['response']
        self.interval = self.data['interval']
        self.min_chat = self.data['min_chat']
        self.is_also_command = self.data['is_also_command']
        self.alternate = self.data['alternate']
        self.timestamp = self.data['timestamp']


class Timers(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.all_timers = None
        self.timestamp = None
        self.messages_sent = {}

    async def create_task(self, func:callable, *args, **kwargs):
        """
        Creates an async task for a function.
        :param func:
        :param args:
        :param kwargs:
        :return:
        """

        return await asyncio.create_task(func(*args, **kwargs))

    def dict_from_row(self, row):
        """
        Converts a row from the database to a dictionary.
        :param row:
        :return: list of dictionaries
        """
        lists_of_dicts = []
        for i in row:
            lists_of_dicts.append(Timer(i))
        print(lists_of_dicts)
        return lists_of_dicts

    async def cache_timers(self):
        """
        Caches all timers.
        :return:
        """
        self.all_timers = await self.bot.db.fetch('SELECT * FROM timers')
        self.all_timers = self.dict_from_row(self.all_timers)
        return self.all_timers


    async def function_worker(self):
        """
        Creates a task for each timer.
        :return:
        """
        await self.bot.wait_for_ready()
        count = 0
        start = time.time()
        while True:
            current_timestamp = int(datetime.utcnow().timestamp())
            for i, timer_event in enumerate(self.all_timers):
                if 'last_used' in timer_event.keys() and timer_event['last_used'] + timer_event['interval'] > current_timestamp:
                    continue

                timer_event['last_used'] = current_timestamp
                self.all_timers[i] = timer_event
                channel = self.bot.get_channel(timer_event['channel'])
                end = time.time()
                count += 1
                await channel.send(f"Count: {count} | Time:{round(end-start, 2)} | {timer_event['response']}")
            await asyncio.sleep(2.5)

    async def cache_message_count(self, channel: twitchio.Channel):
        if channel.name not in self.messages_sent.keys():
            self.messages_sent[channel.name] = 0
        else:
            self.messages_sent[channel.name] += 1


    @commands.Cog.event()
    async def event_message(self, message):
        if message.echo:
            return

        await self.cache_message_count(message.channel)
        print(self.messages_sent[message.channel.name])
        await self.bot.handle_commands(message)


    @commands.Cog.event()
    async def event_ready(self):
        await self.create_task(self.cache_timers)
        await self.create_task(self.function_worker)


    @commands.command()
    async def add_timer(self, ctx: commands.Context, name, interval, min_chat, is_also_command, *, response):
        await self.bot.db.execute('INSERT INTO timers (name, interval, min_chat, is_also_command, response) VALUES (?, ?, ?, ?, ?)',
                                  [name, interval, min_chat, is_also_command, response])
        await ctx.send(f'Timer {name} has been added.')

def prepare(bot: commands.Bot):
    bot.add_cog(Timers(bot))