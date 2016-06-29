import os

import config
from alphahome.models import db
from flask import Flask, render_template
from flask_debugtoolbar import DebugToolbarExtension


def create_app():
    """
    :return: Flask App

    Flask App 생성
    """
    current_dir = os.path.abspath(os.path.dirname(__file__))
    template_folder = os.path.join(current_dir, 'templates')

    app = Flask(__name__, template_folder=template_folder)
    app.jinja_env.auto_reload = True
    app.jinja_env.autoescape = False
    config.init_app(app)
    db.init_app(app)

    toolbar = DebugToolbarExtension()
    toolbar.init_app(app)

    # Application Blueprints
    from alphahome.views.main import main as main_blueprint
    from alphahome.views.interior import interior as interior_blueprint
    from alphahome.views.snapshot import snapshot as snapshot_blueprint
    from alphahome.views.magazine import magazine as magazine_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(interior_blueprint, url_prefix='/interior')
    app.register_blueprint(snapshot_blueprint, url_prefix='/snapshot')
    app.register_blueprint(magazine_blueprint, url_prefix='/magazine')

    app.errorhandler(404)(lambda e: render_template('error/404.html'))

    return app
