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
    config.init_app(app)
    db.init_app(app)

    toolbar = DebugToolbarExtension()
    toolbar.init_app(app)

    # Application Blueprints
    from alphahome.views.main import main as main_blueprint
    from alphahome.views.snapshot import snapshot as snapshot_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(snapshot_blueprint, url_prefix='/snapshot')

    app.errorhandler(404)(lambda e: render_template('error/404.html'))

    return app
