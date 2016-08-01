from flask import Blueprint, render_template, request, redirect, url_for, current_app
from flask import session
from happyathome.forms import Pagination
from happyathome.models import db, User, Professional, Magazine, Category, Residence, Photo, PhotoScrap, Comment

professionals = Blueprint('professionals', __name__)


@professionals.context_processor
def utility_processor():
    def url_for_s3(s3path, filename=''):
        return ''.join((current_app.config['S3_BUCKET_NAME'], current_app.config[s3path], filename))
    return dict(url_for_s3=url_for_s3)


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
    user = db.session.query(User).filter_by(id=id).first()
    professional = db.session.query(Professional).filter(Professional.user_id == user.id).first()
    magazines = db.session.query(Magazine).filter(Magazine.user_id == user.id).order_by(Magazine.id.desc()).limit(4).all()

    return render_template(current_app.config['TEMPLATE_THEME'] + '/professionals/detail.html',
                           user=user,
                           professional=professional,
                           current_app=current_app, magazines=magazines)


@professionals.route('/<id>/story', defaults={'page': 1})
@professionals.route('/<id>/story/page/<int:page>')
def story(id, page):
    user = db.session.query(User).filter_by(id=id).first()
    magazines = db.session.query(Magazine).filter(Magazine.user_id == user.id).order_by(Magazine.id.desc())
    magazines_count = magazines.count()
    pagination = Pagination(page, 6, magazines.count())

    if page != 1:
        offset = 6 * (page - 1)
    else:
        offset = 0
    magazines = magazines.limit(6).offset(offset).all()

    return render_template(current_app.config['TEMPLATE_THEME'] + '/professionals/story.html', user=user,
                           current_app=current_app, magazines=magazines, pagination=pagination,
                           magazines_count=magazines_count)


@professionals.route('/<id>/gallery', defaults={'page': 1})
@professionals.route('/<id>/gallery/page/<int:page>')
def gallery(id, page):
    user = db.session.query(User).filter_by(id=id).first()
    photos = db.session.query(Photo).filter(Photo.user_id == user.id).order_by(Photo.id.desc())
    pagination = Pagination(page, 8, photos.count())

    if session:
        if session['user_id'] == user.id:
            photos = photos.limit(4).all()
            return render_template(current_app.config['TEMPLATE_THEME'] + '/professionals/gallery.html',
                                   user=user,
                                   photos=photos,
                                   pagination=pagination,
                                   current_app=current_app)

    if page != 1:
        offset = 6 * (page - 1)
    else:
        offset = 0
    photos = photos.limit(12).offset(offset).all()
    return render_template(current_app.config['TEMPLATE_THEME'] + '/professionals/gallery.html',
                           user=user,
                           photos=photos,
                           current_app=current_app,
                           pagination=pagination)


@professionals.route('/<id>/question')
def question(id):
    user = db.session.query(User).filter_by(id=id).first()
    story_qna = Magazine.query.filter(Magazine.comments.any(Comment.user_id == id)).all()
    gallery_qna = Comment.query.filter(Comment.user_id == id).filter(Comment.photos.any(comment_id=Comment.id)).all()
    return render_template(current_app.config['TEMPLATE_THEME'] + '/professionals/question.html',
                           user=user,
                           story_qna=story_qna,
                           gallery_qna=gallery_qna)


@professionals.route('/<id>/scrap')
def scrap(id):
    user = db.session.query(User).filter_by(id=id).first()
    photoscraps = db.session.query(PhotoScrap).filter(PhotoScrap.user_id == user.id)
    photoscrap_count = photoscraps.count()
    photoscraps = photoscraps.all()

    return render_template(current_app.config['TEMPLATE_THEME'] + '/professionals/scrap.html',
                           user=user,
                           photoscraps=photoscraps,
                           photoscrap_count=photoscrap_count,
                           current_app=current_app)
