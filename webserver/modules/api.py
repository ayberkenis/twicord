from quart import Blueprint, flash, g, redirect, render_template, request, url_for, session
from utils.dbcontrol import Database
import os
import aiohttp
import base64

bp = Blueprint('api', __name__)
db = Database()

async def refresh_access_token():
    credentials = await db.get_credentials()

    params = {"grant_type": "refresh_token", "refresh_token": credentials['spotify_refresh_token']}
    auth_str = f"{os.environ['spotify_client_id']}:{os.environ['spotify_secret']}"
    authorization = base64.urlsafe_b64encode(auth_str.encode()).decode()
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Authorization': f'Basic {authorization}'}
    async with aiohttp.ClientSession() as session:
        async with session.post(f"https://accounts.spotify.com/api/token", headers=headers, params=params) as response:
            print(await response.text())
            data = await response.json()
            print(data)
            access_token = data['access_token']
    await db.insert_or_update('credentials', spotify_access_token=access_token, spotify_refresh_token=credentials['spotify_refresh_token'])
    return access_token

async def code_to_access_token(code):
    params = {"grant_type": "authorization_code", "code": code, "redirect_uri": os.environ['spotify_redirect_uri'],
              "client_id": os.environ['spotify_client_id'], "client_secret": os.environ['spotify_secret']}
    auth_str = f"{os.environ['spotify_client_id']}:{os.environ['spotify_secret']}"
    authorization = base64.urlsafe_b64encode(auth_str.encode()).decode()
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Authorization': f'Basic {authorization}'}
    async with aiohttp.ClientSession() as session:
        async with session.post(f"https://accounts.spotify.com/api/token", headers=headers, params=params) as response:
            data = await response.json()
            await db.insert_or_update('credentials', spotify_access_token=data['access_token'], spotify_refresh_token=data['refresh_token'])
            # await db.insert_or_update('credentials', spotify_refresh_token=data['refresh_token'])
            return data['access_token']

@bp.route('/callback', methods=['GET', 'POST'])
async def callback():
    code = request.args['code']
    print(code)
    await code_to_access_token(code)
    await db.insert_or_update('credentials', spotify_code=code)
    return code

@bp.route('/refresh', methods=['GET', 'POST'])
async def refresh():
    new_ = await refresh_access_token()
    return f'Refreshed old access token, new token: {new_}'