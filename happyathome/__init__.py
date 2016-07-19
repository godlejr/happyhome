import os
import config
from flask_admin import Admin
from happyathome.models import db, User, File, Photo, Magazine, MagazineComment, PhotoComment, Comment
from flask import Flask, render_template
from flask_debugtoolbar import DebugToolbarExtension
from happyathome.views.admin import MyView, UserAdmin, ClassAdminMagazine, ClassAdminPhoto, CommentAdminFile


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

    toolbar = DebugToolbarExtension()
    toolbar.init_app(app)

    # admin
    admin = Admin(app, name='Happy@Home', template_mode='bootstrap3')
    admin.add_view(UserAdmin(User, db.session, name='사용자관리'))

    admin.add_view(ClassAdminPhoto(Photo, db.session, name='포토', category='분류관리'))
    admin.add_view(ClassAdminMagazine(Magazine, db.session, name='매거진', category='분류관리'))
    admin.add_view(CommentAdminFile(Comment, db.session, name='댓글', category='댓글관리'))

    # admin.add_view(ClassAdmin(db.session.query(File).join(Magazine).filter(Magazine.file_id==File.id),\
    #                         db.session, name='매거진',  category='분류관리'))

    # Application Blueprints
    from happyathome.views.main import main as main_blueprint
    from happyathome.views.photos import photos as photos_blueprint
    from happyathome.views.magazines import magazines as magazines_blueprint
    from happyathome.views.professionals import professionals as pros_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(magazines_blueprint, url_prefix='/magazines')
    app.register_blueprint(photos_blueprint, url_prefix='/photos')
    app.register_blueprint(pros_blueprint, url_prefix='/professionals')

    app.errorhandler(404)(lambda e: render_template('error/404.html'))

    return app
