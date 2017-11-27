from flask import Flask, render_template
from flask_mail import Mail
from flask_moment import Moment
from config import config


moment = Moment()
mail = Mail()


# THE APP
def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    moment.init_app(app)
    mail.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
