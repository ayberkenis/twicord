from quart import Blueprint, flash, g, redirect, render_template, request, url_for, session


bp = Blueprint('ui', __name__)

@bp.route('/')
async def index():
    return await render_template('index.html')


@bp.route('/setup')
async def setup_twicord():
    return await render_template('setup.html')