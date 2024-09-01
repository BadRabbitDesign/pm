#main
from flask_login import LoginManager
from flask import Blueprint



login_manager=LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'main.login'

main = Blueprint('main',__name__)
from . import views




@main.record_once
def on_load(state):
    login_manager.init_app(state.app)
    
    if state.app.debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)
        logging.info('Started')
