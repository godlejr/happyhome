from flask import Blueprint, render_template, request, redirect, url_for, current_app
from happyathome.forms import Pagination
from happyathome.models import db, User, Professional

pros = Blueprint('professionals', __name__)


@pros.route('/',defaults={'page': 1})
@pros.route('/page/<int:page>')
def list(page):
    posts = db.session.query(Professional)
    pagination = Pagination(page, 2, posts.count())
    count=posts.count()
    return render_template(current_app.config['TEMPLATE_THEME'] + '/professionals/list.html',posts=posts, current_app=current_app,pagination=pagination,count=count)


@pros.route('/<id>')
def detail(id):
    post = db.session.query(Professional).filter_by(id=id).first()
    return render_template(current_app.config['TEMPLATE_THEME'] + '/professionals/detail.html', post=post)
