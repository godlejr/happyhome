import os
import config
from flask import Flask, render_template
from flask_login import LoginManager
from flask_debugtoolbar import DebugToolbarExtension
from happyathome.models import db, User


def create_app(config_name):
    """
    :return: Flask App

    Flask App 생성
    """
    current_dir = os.path.abspath(os.path.dirname(__file__))
    template_folder = os.path.join(current_dir, 'templates')

    app = Flask(__name__, template_folder=template_folder)
    app.jinja_env.auto_reload = True
    app.jinja_env.autoescape = False
    config.init_app(app, config_name)
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)

    toolbar = DebugToolbarExtension()
    toolbar.init_app(app)

    @login_manager.user_loader
    def user_loader(user_id):
        return User.query.get(user_id)

    # Application Blueprints
    from happyathome.views.main import main as main_blueprint
    from happyathome.views.photos import photos as photos_blueprint
    from happyathome.views.magazines import magazines as magazines_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(magazines_blueprint, url_prefix='/magazines')
    app.register_blueprint(photos_blueprint, url_prefix='/photos')

    app.errorhandler(404)(lambda e: render_template('error/404.html'))

    return app
