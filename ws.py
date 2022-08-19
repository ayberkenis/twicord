from utils.dbcontrol import Database
import aiohttp
import base64
import os
from quart import Quart, request, render_template
import logging
from quart.logging import default_handler


quart = Quart(__name__, template_folder='webserver/templates', static_folder='webserver/static')
db = Database()
quartlogger = logging.getLogger('quart.app')
quartlogger.removeHandler(default_handler)
quartlogger.setLevel(logging.DEBUG)
fh = logging.FileHandler('logs/webserver.log')  # Log to file

quart.logger.addHandler(fh)



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
    await db.execute('UPDATE credentials SET spotify_access_token = ? WHERE username="ayberkenis_bot"',
                          (access_token,))
    await db.execute('UPDATE credentials SET spotify_refresh_token = ? WHERE username="ayberkenis_bot"',
                     (credentials['spotify_refresh_token'],))
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
            await db.execute('UPDATE credentials SET spotify_access_token = ? WHERE username="ayberkenis_bot"',
                                  (data['access_token'],))
            await db.execute('UPDATE credentials SET spotify_refresh_token = ? WHERE username="ayberkenis_bot"',
                                  (data['refresh_token'], ))
            return data['access_token']


@quart.route('/')
async def index():
    return await render_template('index.html')

@quart.route('/setup')
async def setup_twicord():
    return await render_template('setup.html')

@quart.route('/callback', methods=['GET', 'POST'])
async def callback():
    code = request.args['code']
    print(code)
    await code_to_access_token(code)
    await db.execute('UPDATE credentials SET spotify_code = ?', (code,))
    return code

@quart.route('/refresh', methods=['GET', 'POST'])
async def refresh():
    new_ = await refresh_access_token()
    return f'Refreshed old access token, new token: {new_}'

quart.run(port=5000)

