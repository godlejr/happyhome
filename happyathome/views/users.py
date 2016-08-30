import base64
import os

import boto3
import shortuuid

from flask import Blueprint, render_template, request, redirect, url_for, current_app, jsonify, session, flash
from flask_login import login_required, current_user
from happyathome.forms import Pagination, UpdateForm, PasswordUpdateForm, ProfessionalUpdateForm
from happyathome.models import db, User, Photo, Magazine, Professional, Follow, PhotoScrap, Comment, MagazineScrap, \
    Business
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

users = Blueprint('users', __name__)


@users.context_processor
def utility_processor():
    def url_for_s3(s3path, filename):
        return ''.join((current_app.config['S3_BUCKET_NAME'], current_app.config[s3path], filename))
    return dict(url_for_s3=url_for_s3)


@users.route('/')
@users.route('/<id>')
def info(id=None):
    if not id:
        if current_user.get_id():
            return redirect(url_for('users.info', id=current_user.id))
        else:
            return redirect(url_for('main.login', next=url_for('users.info')))

    user = User.query.filter_by(id=id).first()
    if user.is_pro:
        return redirect(url_for('professionals.detail', id=id))

    magazine_count =  Magazine.query.filter_by(user_id=id).count()
    photo_count = Photo.query.filter_by(user_id=id).count()
    photoscrap_count = PhotoScrap.query.filter_by(user_id=id).count()
    following_count = Follow.query.filter_by(user_id=id).count()
    follower_count = Follow.query.filter_by(follow_id=id).count()
    comment_count = Comment.query.filter_by(user_id=id, deleted=0, depth=0).count()

    magazine_question_count = Comment.query. \
        filter(Comment.deleted == 0). \
        filter(Comment.depth == 0). \
        filter(Comment.user_id != id). \
        filter(Comment.magazines.any(Magazine.user_id == id)). \
        count()

    photo_question_count = Comment.query. \
        filter(Comment.deleted == 0). \
        filter(Comment.depth == 0). \
        filter(Comment.user_id != id). \
        filter(Comment.photos.any(Photo.user_id == id)). \
        count()

    question_count = magazine_question_count + photo_question_count

    return render_template(current_app.config['TEMPLATE_THEME'] + '/users/info.html',
                           user=user,
                           magazine_count=magazine_count,
                           photo_count=photo_count,
                           photoscrap_count=photoscrap_count,
                           following_count=following_count,
                           follower_count=follower_count,
                           comment_count=comment_count,
                           question_count=question_count)


@users.route('/<id>/gallery', defaults={'page': 1})
@users.route('/<id>/gallery/page/<int:page>')
def gallery(id, page):
    user = User.query.filter_by(id=id).first()

    page_offset = 9 if 'user_id' in session and session['user_id'] == user.id else 10
    photos = Photo.query.filter_by(user_id=user.id)
    photos_count = photos.count()

    offset = (page_offset * (page - 1)) if page != 1 else 0
    pagination = Pagination(page, page_offset, photos.count())
    photos = photos.order_by(Photo.id.desc()).limit(page_offset).offset(offset).all()

    return render_template(current_app.config['TEMPLATE_THEME'] + '/users/gallery.html',
                           user=user,
                           photos=photos,
                           photos_count=photos_count,
                           pagination=pagination)


@users.route('/<id>/story', defaults={'page': 1})
@users.route('/<id>/story/page/<int:page>')
def story(id, page):
    offset = (10 * (page - 1)) if page != 1 else 0
    user = User.query.filter_by(id=id).first()
    magazines = Magazine.query.filter_by(user_id=user.id)
    pagination = Pagination(page, 10, magazines.count())
    magazines_count = magazines.count()
    magazines = magazines.order_by(Magazine.id.desc()).limit(10).offset(offset).all()

    return render_template(current_app.config['TEMPLATE_THEME'] + '/users/story.html',
                           user=user,
                           magazines=magazines,
                           magazines_count=magazines_count,
                           pagination=pagination)


@users.route('/<id>/follow')
def follow(id):
    user = User.query.filter_by(id=id).first()
    followings = Follow.query.filter_by(user_id=id).limit(8).all()
    followers = Follow.query.filter_by(follow_id=id).limit(8).all()

    return render_template(current_app.config['TEMPLATE_THEME'] + '/users/follow.html',
                           user=user,
                           followers=followers,
                           followings=followings)


@users.route('/<id>/follower')
def user_follower(id):
    user = User.query.filter_by(id=id).first()
    followers = Follow.query.filter_by(follow_id=id).all()

    return render_template(current_app.config['TEMPLATE_THEME'] + '/users/follower.html',
                           user=user,
                           followers=followers)


@users.route('/<id>/following')
def user_following(id):
    user = User.query.filter_by(id=id).first()
    followings = Follow.query.filter_by(user_id=id).all()

    return render_template(current_app.config['TEMPLATE_THEME'] + '/users/following.html',
                           user=user,
                           followings=followings)


@users.route('/<id>/scrap')
def scrap(id):
    user = User.query.filter_by(id=id).first()

    magazinescraps = MagazineScrap.query.filter_by(user_id=user.id)
    magazinescraps_count = magazinescraps.count()
    magazinescraps = magazinescraps.order_by(MagazineScrap.id.desc()).limit(10).all()

    photoscraps = PhotoScrap.query.filter_by(user_id=user.id)
    photoscraps_count = photoscraps.count()
    photoscraps = photoscraps.order_by(PhotoScrap.id.desc()).limit(10).all()

    return render_template(current_app.config['TEMPLATE_THEME'] + '/users/scrap.html',
                           user=user,
                           magazinescraps=magazinescraps,
                           magazinescraps_count=magazinescraps_count,
                           photoscraps=photoscraps,
                           photoscraps_count=photoscraps_count)


@users.route('/<id>/scrap/story', defaults={'page': 1})
@users.route('/<id>/scrap/story/page/<int:page>')
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


@users.route('/<id>/scrap/gallery', defaults={'page': 1})
@users.route('/<id>/scrap/gallery/page/<int:page>')
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


@users.route('/<id>/question')
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

    return render_template(current_app.config['TEMPLATE_THEME'] + '/users/question.html',
                           user=user,
                           story_qna=story_qna,
                           story_count=story_count,
                           gallery_count=gallery_count,
                           gallery_qna=gallery_qna,
                           current_app=current_app)


@users.route('/<id>/edit_professional_info', methods=['GET', 'POST'])
@login_required
def edit_professional_info(id):
    user = User.query.filter_by(id=id).first()
    professional = Professional.query.filter_by(user_id=id).first()
    businesses = Business.query.all()
    form = ProfessionalUpdateForm(request.form)

    if request.method == 'POST':
        if form.validate():
            if request.form.get('business_id').__eq__(""):
                flash('업종을 선택하세요.')
            else:
                user.name = form.name.data
                professional.business_no = form.business_no.data
                professional.homepage = form.homepage.data
                professional.address = form.address.data
                professional.sub_address = form.sub_address.data
                professional.phone = form.phone.data
                professional.greeting = request.form.get('greeting')
                professional.sido_code = request.form['sigungucode'][:2]
                professional.sigungu_code = request.form['sigungucode']
                professional.post_code = request.form['postcode']
                professional.business_id = request.form.get('business_id')
                professional.sido = request.form['sido']
                professional.sigungu = request.form['sigungu']
                db.session.add(user)
                db.session.add(professional)
                db.session.commit()

                return redirect(url_for('users.edit_profile', id=id))

    return render_template(current_app.config['TEMPLATE_THEME'] + '/users/edit_professional_info.html',
                           user=user,
                           businesses=businesses,
                           form=form)


@users.route('/<id>/edit_professional', methods=['GET', 'POST'])
@login_required
def edit_professional(id):
    user = User.query.filter_by(id=id).first()
    professional = Professional()
    businesses = Business.query.all()
    form = ProfessionalUpdateForm(request.form)

    if request.method == 'POST':
        if form.validate():
            if request.form.get('business_id').__eq__(""):
                flash('업종을 선택하세요.')
            else:
                user.name = form.name.data
                user.level = 2
                professional.user_id = id
                professional.business_no = form.business_no.data
                professional.homepage = form.homepage.data
                professional.address = form.address.data
                professional.sub_address = form.sub_address.data
                professional.phone = form.phone.data
                professional.greeting = request.form.get('greeting')
                professional.post_code = request.form['postcode']

                if not request.form['business_id'].__eq__(""):
                    professional.business_id = request.form['business_id']

                professional.sido_code = request.form['sigungucode'][:2]
                professional.sigungu_code = request.form['sigungucode']
                professional.sido = request.form['sido']
                professional.sigungu = request.form['sigungu']
                db.session.add(user)
                db.session.add(professional)
                db.session.commit()

                return redirect(url_for('users.edit_profile', id=id))

    return render_template(current_app.config['TEMPLATE_THEME'] + '/users/edit_professional.html',
                           user=user,
                           businesses=businesses,
                           form=form)


@users.route('/<id>/password/edit', methods=['GET', 'POST'])
@login_required
def edit_password(id):
    user = User.query.filter_by(id=id).first()
    form = PasswordUpdateForm(request.form)
    if request.method == 'POST':
        if form.validate():
            user.password = generate_password_hash(form.password.data)
            db.session.add(user)
            db.session.commit()

            return redirect(url_for('users.edit_profile', id=id))

    return render_template(current_app.config['TEMPLATE_THEME'] + '/users/edit_password.html', user=user, form=form)


@users.route('/<id>/edit', methods=['GET', 'POST'])
@login_required
def edit_profile(id):
    user = User.query.filter_by(id=session['user_id']).first()
    form = UpdateForm(request.form)
    if request.method == 'POST':
        user.name = form.name.data

        if request.form['sex_check'] == '1':
            user.sex = 'M'
        else:
            user.sex = 'F'

        if user.avatar != request.form.get('profileFileName'):
            if user.avatar != 'avatar.png':
                s3 = boto3.resource('s3')
                s3.Object('static.inotone.co.kr', 'data/user/%s' % user.avatar).delete()

        user.avatar = request.form.get('profileFileName')

        if user.cover != request.form.get('coverFileName'):
            if user.cover != 'cover.jpg':
                s3 = boto3.resource('s3')
                s3.Object('static.inotone.co.kr', 'data/cover/%s' % user.cover).delete()

        user.cover = request.form.get('coverFileName')

        db.session.add(user)
        db.session.commit()
        return redirect(url_for('users.edit_profile', id=id))
    return render_template(current_app.config['TEMPLATE_THEME'] + '/users/edit_profile.html', user=user, form=form)


@users.route('/profile_upload', methods=['POST'])
@login_required
def profile_upload():
    if request.method == "POST":
        photo_data = request.form.get('file_data').split(',')[1]
        photo_name = secure_filename(
            ''.join((shortuuid.uuid(), os.path.splitext(request.form.get('file_name'))[1])))

        s3 = boto3.resource('s3')
        s3.Object('static.inotone.co.kr', 'data/user/%s' % photo_name).put(Body=base64.b64decode(photo_data),
                                                                           ContentType='image/jpeg')
        return jsonify({
            'file_name': photo_name
        })


@users.route('/profile_unload', methods=['POST'])
@login_required
def profile_unload():
    if request.form.get('pre_file_name') != request.form.get('file_name'):
        s3 = boto3.resource('s3')
        s3.Object('static.inotone.co.kr', 'data/user/%s' % request.form.get('file_name')).delete()

    return jsonify({
        'file_name': request.form.get('file_name')
    })


@users.route('/cover_upload', methods=['POST'])
@login_required
def cover_upload():
    if request.method == "POST":
        photo_data = request.form.get('file_data').split(',')[1]
        photo_name = secure_filename(
            ''.join((shortuuid.uuid(), os.path.splitext(request.form.get('file_name'))[1])))

        s3 = boto3.resource('s3')
        s3.Object('static.inotone.co.kr', 'data/cover/%s' % photo_name).put(Body=base64.b64decode(photo_data),
                                                                            ContentType='image/jpeg')
        return jsonify({
            'file_name': photo_name
        })


@users.route('/cover_unload', methods=['POST'])
@login_required
def cover_unload():
    if request.form.get('pre_file_name') != request.form.get('file_name'):
        s3 = boto3.resource('s3')
        s3.Object('static.inotone.co.kr', 'data/cover/%s' % request.form.get('file_name')).delete()

    return jsonify({
        'file_name': request.form.get('file_name')
    })


@users.route('/following', methods=['POST'])
@login_required
def following():
    if request.method == 'POST':
        follow = Follow.query.filter_by(user_id=session['user_id']).filter_by(follow_id=request.form.get('follow_id'))
        follow_check = follow.first()

        if follow_check:
            ok = -1
            follow.delete()
        else:
            ok = 1
            follow = Follow()
            follow.user_id = session['user_id']
            follow.follow_id = request.form.get('follow_id')

            db.session.add(follow)
        db.session.commit()
        return jsonify({
            'ok': ok
        })
