from flask import Blueprint, render_template, current_app
from flask import session
from happyathome.forms import Pagination
from happyathome.models import db, User, Professional, Magazine, Photo, PhotoScrap, Comment, MagazineScrap

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
    pagination = Pagination(page, 6, posts.count())
    if page != 1:
        offset = 6 * (page - 1)
    else:
        offset = 0

    posts = posts.order_by(Professional.id.desc()).limit(6).offset(offset).all()
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
    user = User.query.filter_by(id=id).first()
    story_qna = db.session.execute('''
        SELECT	cm.id
        ,		cm.group_id
        ,		cm.depth
        ,		cm.sort
        ,		cm.content
        ,		mz.id       as  magazine_id
        ,		mz.title    as  magazine_title
        ,		pf.name     as  file_name
        FROM	comments	cm
        ,		magazines	mz
        ,		(	SELECT	ph.magazine_id
                    ,		fi.name
                    FROM	files	fi
                    ,		photos	ph
                    ,		(	SELECT	magazine_id
                                ,		MIN(id)	id
                                FROM	photos
                                GROUP
                                BY		magazine_id
                            )	pt
                    WHERE	ph.id		=	pt.id
                    AND		ph.file_id	=	fi.id
                )	pf
        WHERE	mz.id	    =	pf.magazine_id
        AND		cm.deleted	=	0
        AND		EXISTS	(	SELECT	1
                            FROM	magazine_comments	mc
                            WHERE	mc.magazine_id	=	mz.id
                            AND		mc.comment_id	=	cm.id
                        )
        AND		EXISTS	(	SELECT	1
                            FROM	comments	re
                            WHERE	re.group_id	=	cm.group_id
                            AND		re.user_id	=	%s
                            AND		re.depth	>	0
                            GROUP
                            BY		re.group_id
                        )
        ORDER
        BY			cm.group_id	DESC
        ,			cm.depth	ASC
        ,			cm.sort		ASC
        ,			cm.id		ASC
    ''' % id)
    gallery_qna = db.session.execute('''
            SELECT	cm.id
            ,		cm.group_id
            ,		cm.depth
            ,		cm.sort
            ,		cm.content
            ,		ph.id       as  photo_id
            ,		fi.name     as  file_name
            FROM	comments	cm
            ,		photos  	ph
            ,       files       fi
            WHERE	ph.file_id  =   fi.id
            AND     cm.deleted	=	0
            AND		EXISTS	(	SELECT	1
                                FROM	photo_comments	pc
                                WHERE	pc.photo_id     =	ph.id
                                AND		pc.comment_id	=	cm.id
                            )
            AND		EXISTS	(	SELECT	1
                                FROM	comments	re
                                WHERE	re.group_id	=	cm.group_id
                                AND		re.user_id	=	%s
                                AND		re.depth	>	0
                                GROUP
                                BY		re.group_id
                            )
            ORDER
            BY			cm.group_id	DESC
            ,			cm.depth	ASC
            ,			cm.sort		ASC
            ,			cm.id		ASC
        ''' % id)
    return render_template(current_app.config['TEMPLATE_THEME'] + '/professionals/question.html',
                           user=user,
                           story_qna=story_qna,
                           gallery_qna=gallery_qna)


@professionals.route('/<id>/scrap')
def scrap(id):
    user = User.query.filter_by(id=id).first()
    magazinescraps = MagazineScrap.query.filter_by(user_id=user.id)
    magazinescraps_count = magazinescraps.count()
    magazinescraps = magazinescraps.order_by(MagazineScrap.id.desc()).limit(10).all()

    photoscraps = PhotoScrap.query.filter_by(user_id=user.id)
    photoscraps_count = photoscraps.count()
    photoscraps = photoscraps.order_by(PhotoScrap.id.desc()).limit(10).all()

    return render_template(current_app.config['TEMPLATE_THEME'] + '/professionals/scrap.html',
                           user=user,
                           photoscraps=photoscraps,
                           photoscraps_count=photoscraps_count,
                           magazinescraps=magazinescraps,
                           magazinescraps_count=magazinescraps_count)



@professionals.route('/<id>/scrap/story', defaults={'page': 1})
@professionals.route('/<id>/scrap/story/page/<int:page>')
def scrap_story(id, page):
    offset = (10 * (page - 1)) if page != 1 else 0
    user = User.query.filter_by(id=id).first()

    magazinescraps = MagazineScrap.query.filter_by(user_id=user.id)
    magazinescraps_count = magazinescraps.count()
    magazinescraps = magazinescraps.order_by(MagazineScrap.id.desc()).limit(10).offset(offset).all()

    pagination = Pagination(page, 10, magazinescraps_count)

    return render_template(current_app.config['TEMPLATE_THEME'] + '/users/scrap_story.html',
                           user=user,
                           pagination=pagination,
                           magazinescraps=magazinescraps,
                           magazinescraps_count=magazinescraps_count)


@professionals.route('/<id>/scrap/gallery', defaults={'page': 1})
@professionals.route('/<id>/scrap/gallery/page/<int:page>')
def scrap_gallery(id, page):
    offset = (10 * (page - 1)) if page != 1 else 0
    user = User.query.filter_by(id=id).first()

    photoscraps = PhotoScrap.query.filter_by(user_id=user.id)
    photoscraps_count = photoscraps.count()
    photoscraps = photoscraps.order_by(PhotoScrap.id.desc()).limit(10).offset(offset).all()

    pagination = Pagination(page, 10, photoscraps_count)

    return render_template(current_app.config['TEMPLATE_THEME'] + '/users/scrap_gallery.html',
                           user=user,
                           pagination=pagination,
                           photoscraps=photoscraps,
                           photoscraps_count=photoscraps_count)
