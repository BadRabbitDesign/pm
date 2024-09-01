from flask import Flask,render_template
from config import config
from pm2000.dal.database import init_db
from pm2000.app.pm.main import *




from flask_nav import Nav
from flask_nav.elements import Navbar, View

topbar = Navbar('',
    View('<i class="fa fa-home">Home</i>', 'main.project_manager'),
    
)

nav = Nav()

def create_app(config_name):
    app=Flask(__name__)
	
    app.config.from_object(config[config_name])
    init_db()
	
    from pm2000.app.pm.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    
    
    nav.register_element('top', topbar)


    nav.init_app(app)
    
    
    return app







