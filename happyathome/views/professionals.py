import datetime

from flask import Blueprint, render_template, current_app, request, url_for, jsonify
from flask import session
from flask_login import login_required, current_user
from happyathome.forms import Pagination
from happyathome.models import db, User, Professional, Magazine, Photo, PhotoScrap, Comment, MagazineScrap, Review, \
    Business, Sido
from sqlalchemy import func
from werkzeug.utils import redirect

professionals = Blueprint('professionals', __name__)


@professionals.context_processor
def utility_processor():
    def url_for_s3(s3path, filename=''):
        return ''.join((current_app.config['S3_BUCKET_NAME'], current_app.config[s3path], filename))
    return dict(url_for_s3=url_for_s3)


@professionals.route('/', defaults={'page': 1})
@professionals.route('/page/<int:page>')
def list(page):
    area_id = request.args.get('area_id')
    sort_id = request.args.get('sort_id')
    business_id = request.args.get('business_id')
    business = Business.query.filter_by(id=business_id).first()
    businesses = Business.query.all()
    posts = Professional.query

    pagination = Pagination(page, 6, posts.count())
    if page != 1:
        offset = 6 * (page - 1)
    else:
        offset = 0

    if business_id:
        posts = posts.filter(Professional.business_id == business_id).order_by(Professional.id.desc()).limit(6).offset(offset).all()
    elif area_id:
        posts = posts.join(Sido, Professional.sido_code == Sido.sido_code).filter(Sido.area_id == area_id).order_by(Professional.id.desc()).limit(6).offset(offset).all()
    elif sort_id:
        posts = posts.order_by(Professional.id.desc()).limit(6).offset(offset).all()
    else:
        posts = posts.outerjoin(Photo, Photo.user_id == Professional.user_id). \
            group_by(Professional.user_id).order_by(func.count(Photo.id).desc()).limit(6).offset(offset).all()

    return render_template(current_app.config['TEMPLATE_THEME'] + '/professionals/list.html',
                           posts=posts,
                           business=business,
                           businesses=businesses,
                           current_app=current_app,
                           pagination=pagination,
                           query_string=request.query_string.decode('utf-8'))


@professionals.route('/<id>')
def detail(id):
    user = User.query.filter_by(id=id).first()
    professional = Professional.query.filter_by(user_id=user.id).first()
    magazines = Magazine.query.filter_by(user_id=user.id).order_by(Magazine.id.desc()).limit(4).all()

    return render_template(current_app.config['TEMPLATE_THEME'] + '/professionals/detail.html',
                           user=user,
                           professional=professional,
                           current_app=current_app, magazines=magazines)


@professionals.route('/<id>/story', defaults={'page': 1})
@professionals.route('/<id>/story/page/<int:page>')
def story(id, page):
    user = User.query.filter_by(id=id).first()
    magazines = Magazine.query.filter_by(user_id=user.id).order_by(Magazine.id.desc())
    magazines_count = magazines.count()
    pagination = Pagination(page, 15, magazines.count())

    if page != 1:
        offset = 15 * (page - 1)
    else:
        offset = 0
    magazines = magazines.limit(15).offset(offset).all()

    return render_template(current_app.config['TEMPLATE_THEME'] + '/professionals/story.html', user=user,
                           current_app=current_app, magazines=magazines, pagination=pagination,
                           magazines_count=magazines_count)


@professionals.route('/<id>/gallery', defaults={'page': 1})
@professionals.route('/<id>/gallery/page/<int:page>')
def gallery(id, page):
    user = User.query.filter_by(id=id).first()
    photos = Photo.query.filter_by(user_id=user.id).order_by(Photo.id.desc())
    pagination = Pagination(page, 15, photos.count())

    if session:
        if session.get('user_id') == user.id:
            photos = photos.limit(4).all()
            return render_template(current_app.config['TEMPLATE_THEME'] + '/professionals/gallery.html',
                                   user=user,
                                   photos=photos,
                                   pagination=pagination,
                                   current_app=current_app)

    if page != 1:
        offset = 15 * (page - 1)
    else:
        offset = 0
    photos = photos.limit(15).offset(offset).all()
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
        ,		cm.depth    as  depth
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

    story_count = db.session.execute('''
        SELECT	ROUND(((count(distinct cm.id)/2)-0.1),0) as count
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
        SELECT distinct
            pt.id	 as photo_id,
            pt.content 	as photo_content,
            fi.name	as file_name,
            cm.id	as	comment_id,
            cm.content	as	content,
            cm.group_id	as	group_id,
            cm.depth	as	depth,
            cm.created_at	as created_at
        from	comments cm,
                photo_comments pc,
                photos pt,
                files fi,
                users ur
        where 	cm.id = pc.comment_id
        AND		pc.photo_id = pt.id
        AND		pt.file_id = fi.id
        AND 	pt.user_id = %s
        AND		cm.deleted = 0
        AND		cm.group_id = ( SELECT 	re.group_id
                                from 	comments re
                                where 	cm.group_id = re.group_id
                                AND 	re.depth =1	)
        ORDER BY cm.group_id desc,
                cm.depth asc,
                cm.sort	asc
        limit 4
    ''' % id)

    gallery_count = db.session.execute('''
        SELECT ROUND(((count(distinct cm.id)/2)-0.1),0) as count
           from	comments cm,
                   photo_comments pc,
                   photos pt,
                   files fi,
                   users ur
           where 	cm.id = pc.comment_id
           AND		pc.photo_id = pt.id
           AND		pt.file_id = fi.id
           AND 	pt.user_id = %s
           AND		cm.deleted = 0
           AND		cm.group_id = ( SELECT 	re.group_id
                                   from 	comments re
                                   where 	cm.group_id = re.group_id
                                   AND 	re.depth =1	)
           ORDER BY cm.group_id desc,
                   cm.depth asc,
                   cm.sort	asc
       ''' % id)

    return render_template(current_app.config['TEMPLATE_THEME'] + '/professionals/question.html',
                           user=user,
                           story_qna=story_qna,
                           story_count=story_count,
                           gallery_count=gallery_count,
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


@professionals.route('/<id>/review', defaults={'page': 1})
@professionals.route('/<id>/review/page/<int:page>')
def review(id, page):
    user = db.session.query(User).filter_by(id=id).first()
    professional = db.session.query(Professional).filter_by(user_id=user.id).first()
    reviews = db.session.query(Review).filter(Review.professional_id==professional.id).order_by(Review.id.desc())
    pagination = Pagination(page, 6, reviews.count())
    review_count=reviews.count()

    if page != 1:
        offset = 6 * (page - 1)
    else:
        offset = 0

    reviews = reviews.limit(6).offset(offset).all()
    return render_template(current_app.config['TEMPLATE_THEME'] + '/professionals/review.html',
                           professional=professional,
                           reviews=reviews,
                           user=user,
                           current_app=current_app,
                           review_count=review_count,
                           pagination=pagination)


@professionals.route('/<id>/review/new', methods=['GET', 'POST'])
@login_required
def review_new(id):
    if request.method == 'POST':
        professional= Professional.query.filter_by(user_id=id).first()
        if request.form['review_comment'] != "":
            review = Review()
            review.score = request.form['review_star']
            review.content = request.form['review_comment']
            review.professional_id = professional.id
            review.user_id = session['user_id']

            db.session.add(review)
            db.session.commit()

    return redirect(url_for('professionals.review', id=id))


@professionals.route('/review_edit', methods=['POST'])
@login_required
def review_edit():
    if request.method == 'POST':
        if request.form.get('content') != "":
            review = Review.query.filter_by(id=request.form.get('review_id')).first()
            if review.user_id != current_user.id:
                return redirect(url_for('professionals.list'))
            review.content = request.form.get('content')
            db.session.add(review)
            db.session.commit()

            return jsonify({
                'comment': review.content
            })


@professionals.route('/review_remove', methods=['POST'])
@login_required
def review_remove():
    if request.method == 'POST':
        review = Review.query.filter_by(id=request.form.get('review_id')).first()
        if review.user_id != current_user.id:
            return redirect(url_for('professionals.list'))

        db.session.delete(review)
        db.session.commit()

        return jsonify({
            'ok': 1
        })


