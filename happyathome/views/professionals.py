from flask import Blueprint, render_template, request, redirect, url_for, current_app
from happyathome.forms import Pagination
from happyathome.models import db, User, Professional, Magazine, Category, Residence, Photo, PhotoScrap

professionals = Blueprint('professionals', __name__)


@professionals.context_processor
def utility_processor():
    def url_for_s3(s3path, filename):
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
    post = db.session.query(User).filter_by(id=id).first()
    magazines = db.session.query(Magazine).filter(Magazine.user_id == post.id).order_by(Magazine.id.desc())
    magazines_count = magazines.count()
    pagination = Pagination(page, 6, magazines.count())

    if page != 1:
        offset = 6 * (page - 1)
    else:
        offset = 0
    magazines = magazines.limit(6).offset(offset).all()

    return render_template(current_app.config['TEMPLATE_THEME'] + '/professionals/story.html', post=post,
                           current_app=current_app, magazines=magazines, pagination=pagination,
                           magazines_count=magazines_count)


@professionals.route('/<id>/question')
def question(id):
    post = db.session.query(User).filter(User.id == id).first()
    photo_comments = db.session.execute('''
        SELECT  pt.id      AS  id
        ,       pt.content AS	photo_name
        ,       c1.content	AS	question
        ,       c2.content	AS	answer
        ,       fi.name AS file_name
        FROM    comments	c1
        ,       comments	c2
        ,       users		us
        ,       files		fi
        ,       photos		pt
        ,       photo_comments	pc
        WHERE   c1.id	=	c2.comment_id
        AND     c1.id	=	pc.comment_id
        AND     pt.id	=	pc.photo_id
        AND     fi.id	=	pt.file_id
        AND     us.id	=	pt.user_id
        AND     us.id	=	%s limit 2
    ''' % id)

    photo_comments_count = db.session.execute('''
        SELECT  count(*)   AS  count
        FROM    comments	c1
        ,       comments	c2
        ,       users		us
        ,       files		fi
        ,       photos		pt
        ,       photo_comments	pc
        WHERE   c1.id	=	c2.comment_id
        AND     c1.id	=	pc.comment_id
        AND     pt.id	=	pc.photo_id
        AND     fi.id	=	pt.file_id
        AND     us.id	=	pt.user_id
        AND     us.id	=	%s
    ''' % id)

    magazine_comments = db.session.execute('''
        SELECT      mz.id      AS id
            ,       mz.title	AS	photo_name
            ,       c1.content	AS	question
            ,       c2.content	AS	answer
            ,       fi.name 	AS 	file_name
            FROM    comments	c1
            ,       comments	c2
            ,       users		us
            ,       files		fi
            ,       photos		pt
            ,		magazines 	mz
            ,       magazine_comments	mc
            WHERE   c1.id	=	c2.comment_id
            AND     c1.id	=	mc.comment_id
            AND     mz.id	=	mc.magazine_id
            AND     fi.id	=	pt.file_id
            AND 	mz.id	=	pt.magazine_id
            AND     us.id	=	mz.user_id
            AND     us.id	=	%s  limit 2
        ''' % id)

    magazine_comments_count = db.session.execute('''
        SELECT      count(*)    AS  count
            FROM    comments	c1
            ,       comments	c2
            ,       users		us
            ,       files		fi
            ,       photos		pt
            ,		magazines 	mz
            ,       magazine_comments	mc
            WHERE   c1.id	=	c2.comment_id
            AND     c1.id	=	mc.comment_id
            AND     mz.id	=	mc.magazine_id
            AND     fi.id	=	pt.file_id
            AND 	mz.id	=	pt.magazine_id
            AND     us.id	=	mz.user_id
            AND     us.id	=	%s
        ''' % id)

    return render_template(current_app.config['TEMPLATE_THEME'] + '/professionals/question.html',
                           post=post,
                           photo_comments=photo_comments,
                           photo_comments_count=photo_comments_count,
                           magazine_comments=magazine_comments,
                           magazine_comments_count=magazine_comments_count,
                           current_app=current_app)


@professionals.route('/<id>/scrap')
def scrap(id):
    post = db.session.query(User).filter_by(id=id).first()
    photoscraps = db.session.query(PhotoScrap).filter(PhotoScrap.user_id == post.id)
    photoscrap_count = photoscraps.count()
    photoscraps = photoscraps.all()

    return render_template(current_app.config['TEMPLATE_THEME'] + '/professionals/scrap.html', post=post,
                           photoscraps=photoscraps,
                           photoscrap_count=photoscrap_count,
                           current_app=current_app)
