from flask import Blueprint
from flask import Blueprint, render_template, request, redirect, url_for, current_app
from happyathome.forms import Pagination
from happyathome.models import db, User, Photo, Magazine

users = Blueprint('users', __name__)


@users.route('/<id>', defaults={'page': 1})
@users.route('/<id>/page/<int:page>')
def detail(id, page):
    post = db.session.query(User).filter_by(id=id).first()
    photos = db.session.query(Photo).filter(Photo.user_id == post.id).order_by(Photo.id.desc())

    pagination = Pagination(page, 6, photos.count())

    if page != 1:
        offset = 6 * (page - 1)
    else:
        offset = 0
    photos = photos.limit(6).offset(offset).all()

    return render_template(current_app.config['TEMPLATE_THEME'] + '/users/detail.html', post=post, photos=photos,
                           current_app=current_app, pagination=pagination)


@users.route('/detail_list/<id>', defaults={'page': 1})
@users.route('/detail_list/<id>/page/<int:page>')
def detail_list(id, page):
    post = db.session.query(User).filter_by(id=id).first()
    magazines = db.session.query(Magazine).filter(Magazine.user_id == post.id).order_by(Magazine.id.desc())
    pagination = Pagination(page, 6, magazines.count())

    if page != 1:
        offset = 6 * (page - 1)
    else:
        offset = 0
    magazines = magazines.limit(6).offset(offset).all()

    return render_template(current_app.config['TEMPLATE_THEME'] + '/users/detail_list.html', post=post,
                           current_app=current_app, magazines=magazines, pagination=pagination)
