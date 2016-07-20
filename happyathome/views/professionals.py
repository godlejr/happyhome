from flask import Blueprint, render_template, request, redirect, url_for, current_app
from happyathome.forms import Pagination
from happyathome.models import db, User, Professional, Magazine, Category, Residence, Photo

professionals = Blueprint('professionals', __name__)


@professionals.route('/', defaults={'page': 1})
@professionals.route('/page/<int:page>')
def list(page):
    posts = db.session.query(Professional)
    pagination = Pagination(page, 2, posts.count())
    count = posts.count()
    return render_template(current_app.config['TEMPLATE_THEME'] + '/professionals/list.html', posts=posts,
                           current_app=current_app, pagination=pagination, count=count)


@professionals.route('/<id>')
def detail(id):
    post = db.session.query(Professional).filter_by(id=id).first()
    magazines = db.session.query(Magazine).filter(Magazine.user_id == post.user_id)

    media = request.args.get('media') or ''
    category_id = request.args.get('category_id') or ''
    residence_id = request.args.get('residence_id') or ''

    if media:
        magazines = magazines.filter(Magazine.magazine_photos.any(Photo.file.has(type=media)))
    if category_id:
        magazines = magazines.filter(Magazine.category_id == category_id)
    if residence_id:
        magazines = magazines.filter(Magazine.residence_id == residence_id)

    magazines = magazines.order_by(Magazine.id.desc()).all()
    categories = db.session.query(Category).all()
    residences = db.session.query(Residence).all()

    return render_template(current_app.config['TEMPLATE_THEME'] + '/professionals/detail.html', post=post,
                           current_app=current_app, magazines=magazines, categories=categories, residences=residences)
