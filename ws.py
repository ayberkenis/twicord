from utils.dbcontrol import Database
import aiohttp
import base64
import os
from quart import Quart, request, render_template, current_app
import logging
from quart.logging import default_handler
from webserver import modules

quart = Quart(__name__, template_folder='webserver/templates', static_folder='webserver/static')
db = Database()
quartlogger = logging.getLogger('quart.app')
quartlogger.removeHandler(default_handler)
quartlogger.setLevel(logging.DEBUG)
fh = logging.FileHandler('logs/webserver.log')  # Log to file
quart.config['TEMPLATES_AUTO_RELOAD'] = True
quart.logger.addHandler(fh)


for module in modules.bps:
    quart.register_blueprint(module)

quart.run(port=5000)

