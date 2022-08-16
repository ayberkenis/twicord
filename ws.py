from aiohttp import web, request
import aiohttp
app = web.Application()
from utils.dbcontrol import Database
from twitch_cogs.spotify_requests import SpotifyClient
import base64
import os
import json
class WebServer:
    """This class will only be used for Spotify Authorization Code Flow to be able to add songs to the current playback queue."""
    def __init__(self):
        self.client_id = os.environ['spotify_client_id']
        self.client_secret = os.environ['spotify_secret']
        self.redirect_uri = os.environ['spotify_redirect_uri']
        self.code = None
        self.db = Database()
    routes = web.RouteTableDef()

    @routes.get('/callback')
    async def callback_method(self):
        db = Database()
        self.code = self.rel_url.query['code']
        await db.execute('UPDATE credentials SET spotify_code = ?', (self.code,))
        await WebServer().code_to_access_token(self.code)
        return web.Response(text=self.rel_url.query['code'])


    async def code_to_access_token(self, code):
        params = {"grant_type": "authorization_code", "code": code, "redirect_uri": self.redirect_uri, "client_id": self.client_id, "client_secret": self.client_secret}
        auth_str = f"{self.client_id}:{self.client_secret}"
        authorization = base64.urlsafe_b64encode(auth_str.encode()).decode()
        headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Authorization': f'Basic {authorization}'}
        async with aiohttp.ClientSession() as session:
            async with session.post(f"https://accounts.spotify.com/api/token", headers=headers, params=params) as response:
                print(await response.text())
                data = await response.json()
                self.access_token = data['access_token']
        await self.db.execute('UPDATE credentials SET spotify_access_token = ? WHERE username="ayberkenis_bot"', (self.access_token, ))
        return self.access_token



    app.add_routes(routes)

    async def run(self):
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', 5000)
        await site.start()
        print('Webserver has started.')

ws = WebServer()
