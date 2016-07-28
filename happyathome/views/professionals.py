from flask import Blueprint, render_template, request, redirect, url_for, current_app
from happyathome.forms import Pagination
from happyathome.models import db, User, Professional, Magazine, Category, Residence, Photo

professionals = Blueprint('professionals', __name__)


@professionals.route('/', defaults={'page': 1})
@professionals.route('/page/<int:page>')
def list(page):
    posts = db.session.query(Professional)
    pagination = Pagination(page, 2, posts.count())
    if page != 1:
        offset = 2 * (page - 1)
    else:
        offset = 0

    posts = posts.limit(6).offset(offset).all()
    return render_template(current_app.config['TEMPLATE_THEME'] + '/professionals/list.html', posts=posts,
                           current_app=current_app, pagination=pagination)


@professionals.route('/<id>')
def detail(id):
    post = db.session.query(Professional).filter_by(id=id).first()
    magazines = db.session.query(Magazine).filter(Magazine.user_id == post.user_id).order_by(Magazine.id.desc()).limit(
        4).all()

    return render_template(current_app.config['TEMPLATE_THEME'] + '/professionals/gallery.html', post=post,
                           current_app=current_app, magazines=magazines)


@professionals.route('/detail_list/<id>', defaults={'page': 1})
@professionals.route('/detail_list/<id>/page/<int:page>')
def detail_list(id, page):
    post = db.session.query(Professional).filter_by(id=id).first()
    magazines = db.session.query(Magazine).filter(Magazine.user_id == post.user_id).order_by(Magazine.id.desc())
    magazines_count = magazines.count()
    pagination = Pagination(page, 6, magazines.count())

    if page != 1:
        offset = 6 * (page-1)
    else:
        offset = 0
    magazines = magazines.limit(6).offset(offset).all()

    return render_template(current_app.config['TEMPLATE_THEME'] + '/professionals/detail_list.html', post=post,
                           current_app=current_app, magazines=magazines, pagination=pagination,
                           magazines_count=magazines_count)
