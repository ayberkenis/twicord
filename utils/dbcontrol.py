import aiosqlite
import os

class Database:
    def __init__(self):
        dirname = os.path.dirname(__file__)
        self.db_path = os.path.join(os.path.dirname(dirname), 'assets\\twicord.db')



    async def first_setup(self, username, user_id):
        await self.execute('CREATE TABLE IF NOT EXISTS credentials '
                                '(username text PRIMARY KEY, twitch_client_id text, twitch_token text, discord_client_id text, discord_token text, '
                                'spotify_client_id text, spotify_client_secret text, '
                                'spotify_code text, spotify_redirect_uri text, spotify_access_token text, '
                                'spotify_scopes text, spotify_refresh_token text)')
        await self.execute('INSERT OR IGNORE INTO credentials (username, twitch_client_id) VALUES (?, ?)', (username, user_id))

    async def fetch(self, sql):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(sql) as cursor:
                async for row in cursor:
                    return row

    async def execute(self, sql, *params):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(sql, *params)
            await db.commit()