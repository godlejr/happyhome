import os
import config
from flask_admin import Admin
from flask_login import LoginManager
from happyathome.models import db, User, File, Photo, Magazine, MagazineComment, PhotoComment, Comment, Board, Category, \
    Residence, Business
from flask import Flask, render_template
from flask_debugtoolbar import DebugToolbarExtension
from happyathome.lib.redis_session import RedisSessionInterface
from happyathome.views.admin import UserAdmin, ClassAdminMagazine, ClassAdminPhoto, CommentAdminFile, MyAdminIndexView, BoardAdminFile, \
    ClassAdminResidence, ClassAdminCategory, ClassAdminBusiness
from happyathome.views.main import mail
from redis import Redis
from werkzeug.utils import redirect


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
    app.jinja_env.add_extension('jinja2.ext.loopcontrols')

    config.init_app(app, config_name)
    db.init_app(app)
    mail.init_app(app)

    redis = Redis.from_url(app.config['REDIS_URL'])
    app.redis = redis
    app.session_interface = RedisSessionInterface(redis)

    toolbar = DebugToolbarExtension()
    toolbar.init_app(app)

    # admin
    admin = Admin(app, name='Happy@Home', template_mode='bootstrap3', index_view=MyAdminIndexView())
    admin.add_view(UserAdmin(User, db.session, name='사용자관리', endpoint='user'))
    admin.add_view(ClassAdminCategory(Category, db.session, name='테마', category='분류 관리', endpoint='category'))
    admin.add_view(ClassAdminResidence(Residence, db.session, name='장소', category='분류 관리', endpoint='residence'))
    admin.add_view(ClassAdminBusiness(Business, db.session, name='업종', category='분류 관리', endpoint='business'))
    admin.add_view(ClassAdminPhoto(Photo, db.session, name='포토', category='컨텐츠 관리', endpoint='photo'))
    admin.add_view(ClassAdminMagazine(Magazine, db.session, name='매거진', category='컨텐츠 관리', endpoint='magazine'))
    admin.add_view(CommentAdminFile(Comment, db.session, name='댓글', category='댓글 관리', endpoint='comment'))
    admin.add_view(BoardAdminFile(Board, db.session, name='해피QnA', category='댓글 관리',endpoint='board'))

    # Application Blueprints
    from happyathome.views.main import main as main_blueprint
    from happyathome.views.photos import photos as photos_blueprint
    from happyathome.views.magazines import magazines as magazines_blueprint
    from happyathome.views.professionals import professionals as pros_blueprint
    from happyathome.views.boards import boards as boards_blueprint
    from happyathome.views.users import users as users_blueprint
    from happyathome.views.search import search as search_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(magazines_blueprint, url_prefix='/story')
    app.register_blueprint(photos_blueprint, url_prefix='/gallery')
    app.register_blueprint(pros_blueprint, url_prefix='/professional')
    app.register_blueprint(boards_blueprint, url_prefix='/board')
    app.register_blueprint(users_blueprint, url_prefix='/user')
    app.register_blueprint(search_blueprint, url_prefix='/search')

    app.errorhandler(403)(lambda e: redirect('/'))
    app.errorhandler(404)(lambda e: render_template('error/404.html'))
    app.errorhandler(500)(lambda e: render_template('error/404.html'))

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message = '로그인 후 이용해주세요.'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
