import aiosqlite
from aiosqlite import Row
import os

class Database:
    def __init__(self):
        dirname = os.path.dirname(__file__)
        self.db_path = os.path.join(os.path.dirname(dirname), 'assets\\twicord.db')



    async def first_setup(self):
        await self.create_table('credentials', id='varchar', name='TEXT', value='TEXT',
                                timestamp='TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        await self.create_table('channels', name='TEXT', initial='BOOL DEFAULT 0',
                                timestamp='TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        await self.create_table('custom_commands', id='varchar PRIMARY KEY', channel='TEXT', name='TEXT',
                                response='TEXT', cooldown='INTEGER', last_usage_timestamp='TIMESTAMP',
                                timestamp='TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        await self.create_table('settings', id='varchar', channel='TEXT', name='TEXT', value='TEXT',
                                timestamp='TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        await self.create_table('sound_files', id='varchar PRIMARY KEY',channel='TEXT',  command='TEXT',
                                additional_response='TEXT', path='TEXT', volume='INTEGER DEFAULT 50',
                                last_usage_timestamp='TIMESTAMP', timestamp='TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        await self.create_table('timers', id='varchar PRIMARY KEY', channel='TEXT', name='TEXT',
                                response='TEXT', interval='INTEGER', min_chat='INTEGER',
                                is_also_command='INTEGER', alternate='BOOL DEFAULT FALSE',timestamp='TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        await self.create_table('spotify_requests', id='varchar PRIMARY KEY', channel='TEXT', name='TEXT', request='TEXT',
                                requester_username='TEXT', requester_id='TEXT', spotify_uri='TEXT',
                                timestamp='TIMESTAMP DEFAULT CURRENT_TIMESTAMP')

    async def create_table(self, table_name, **kwargs):
        build_str = ', '.join(f'{k} {v}' for k, v in kwargs.items())
        await self.execute(f'CREATE TABLE IF NOT EXISTS {table_name} ({build_str})')


    async def fetch(self, sql, *params):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = Row
            async with db.execute(sql, *params) as cursor:
                return await cursor.fetchall()

    async def execute(self, sql, *params):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = Row
            await db.execute(sql, *params)
            await db.commit()

    async def fetch_value(self, sql, *params):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = Row
            async with db.execute(sql, *params) as cursor:
                return await cursor.fetchone()[0]

    async def get_credentials(self):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = Row
            async with db.execute("SELECT * FROM credentials") as cursor:
                async for row in cursor:
                    return row

