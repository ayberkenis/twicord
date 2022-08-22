import sqlite3
from twitchio.ext import commands
import aiohttp
import uuid
from utils.dbcontrol import Database
from utils import exceptions
import os


class SpotifyTrackObject:
    def __init__(self, data):
        print(data)
        self.data = data['tracks']['items'][0]
        self.external_url = self.data['external_urls']['spotify']
        self.name = self.data['name']
        self.duration_ms = self.data['duration_ms']
        self.artist = self.data['artists'][0]['name']
        self.popularity = self.data['popularity']
        self.id = self.data['id']
        self.track_uri = self.data['uri']


class SpotifyClient:
    def __init__(self):
        self.client_id = os.environ['spotify_client_id']
        self.client_secret = os.environ['spotify_secret']
        self.redirect_uri = os.environ['spotify_redirect_uri']
        self.data = {'grant_type': 'client_credentials',
                     'client_id': self.client_id,
                     'response_type': 'code',
                     'redirect_uri': self.redirect_uri}

        self.access_token = None
        self.scopes = "user-read-currently-playing user-read-playback-state " \
                      "user-read-playback-position " \
                      "user-read-recently-played user-read-playback-position user-modify-playback-state " \
                      "user-read-playback-state user-follow-read"
        self.db = Database()

    async def build_url(self):
        scopes = self.scopes.replace(' ', '%20')
        state = str(uuid.uuid4())[8]
        url = f"https://accounts.spotify.com/authorize?client_id={self.client_id}" \
              f"&response_type=code&redirect_uri={self.redirect_uri}" \
              f"&scope={scopes}&state={state}"
        return url

    async def renew_notification(self, ctx):
        await ctx.send(f"You did not setup Spotify authorization yet. You can use this URL to login and save it.")
        await ctx.send(f"{await self.build_url()}")

    async def renew_access_token(self, refresh_token):
        pass

    async def get_access_token(self):
        try:
            creds = await self.db.get_credentials('spotify_access_token')
            self.access_token = creds
            return self.access_token
        except sqlite3.OperationalError:
            raise exceptions.NoSuchColumn("No such column in database.")

    async def request(self, base_url, access_token=None, endpoint=None, query=None):
        headers = {"Authorization": f"Bearer {await self.get_access_token()}"}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(base_url,
                             headers=headers) as response:
                    return await response.json()
        except Exception as e:
            raise exceptions.RequestError(f"Error while requesting Spotify API: {e}")

    async def get_song(self, ctx, query):
        results = await self.request(f"https://api.spotify.com/v1/search?q={query}&type=track,artist")

        try:
            if 'error' not in results.keys():
                return SpotifyTrackObject(results)
            else:
                await self.renew_notification(ctx)
                raise exceptions.SpotifyAccessTokenExpired(f"Spotify access token has expired. Please renew your access token.")

        except KeyError and exceptions.NoSuchColumn:
            await self.renew_notification(ctx)
            raise exceptions.SpotifySongNotFound(f"Could not find song `{query}` on Spotify API.")

    async def add_item_to_playback_queue(self, ctx, query):
        song = await self.get_song(ctx, query)
        if song:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {await self.get_access_token()}"}
                async with session.post(f'https://api.spotify.com/v1/me/player/queue?uri={song.track_uri}', headers=headers) as response:
                    return song



class SpotifyRequests(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.spotify = SpotifyClient()
        self.db = Database()


    @commands.command()
    async def sr(self, ctx: commands.Context, *, query=None):
        if query:
            song = await self.spotify.add_item_to_playback_queue(ctx, query)
            if song:
                await ctx.send(f'{song.name} has been added to the queue.')
            else:
                await self.spotify.renew_notification(ctx)
        else:
            await ctx.send('You need to declare a song name for me to add it to the queue.')



    @commands.Cog.event()
    async def event_message(self, message):
        if message.echo:
            return

    @commands.Cog.event("event_ready")
    async def event_ready(self):
        pass


def prepare(bot: commands.Bot):
    bot.add_cog(SpotifyRequests(bot))


