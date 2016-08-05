import base64
import os

import boto3
import shortuuid

from flask import Blueprint, render_template, request, redirect, url_for, current_app, jsonify, session
from flask_login import login_required
from happyathome.forms import Pagination, UpdateForm, PasswordUpdateForm, ProfessionalUpdateForm
from happyathome.models import db, User, Photo, Magazine, Professional, Follow, PhotoScrap, Comment, MagazineScrap
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
@login_required
def info(id=None):
    if not id:
        return redirect(url_for('users.info', id=session['user_id']))
    user = User.query.filter_by(id=id).first()
    magazine_count =  Magazine.query.filter_by(user_id=id).count()
    photo_count = Photo.query.filter_by(user_id=id).count()
    photoscrap_count = PhotoScrap.query.filter_by(user_id=id).count()
    following_count = Follow.query.filter_by(user_id=id).count()
    follower_count = Follow.query.filter_by(follow_id=id).count()
    comment_count = Comment.query.filter_by(user_id=id).filter_by(deleted=0).filter_by(depth=0).count()



    return render_template(current_app.config['TEMPLATE_THEME'] + '/users/info.html', user=user,
                           magazine_count=magazine_count, photo_count=photo_count, photoscrap_count=photoscrap_count,
                           following_count=following_count, follower_count=follower_count, comment_count=comment_count
                           )


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

    return render_template(current_app.config['TEMPLATE_THEME'] + '/users/question.html',
                           post=post,
                           photo_comments=photo_comments,
                           photo_comments_count=photo_comments_count,
                           magazine_comments=magazine_comments,
                           magazine_comments_count=magazine_comments_count,
                           current_app=current_app)


@users.route('/<id>/professional/edit', methods=['GET', 'POST'])
def edit_professional(id):
    post = db.session.query(User).filter_by(id=id).first()
    professional = Professional()
    form = ProfessionalUpdateForm(request.form)

    if request.method == 'POST':
        post.name = form.name.data
        post.level = 2
        professional.user_id = id
        professional.business_no = form.business_no.data
        professional.homepage = form.homepage.data
        professional.address = form.address.data
        professional.phone = form.phone.data
        professional.greeting = request.form.get('pro_intro')
        db.session.add(post)
        db.session.add(professional)
        db.session.commit()

        return redirect(url_for('users.edit_info', id=id))

    return render_template(current_app.config['TEMPLATE_THEME'] + '/users/edit_professional.html', post=post,
                           form=form)


@users.route('/<id>/password/edit', methods=['GET', 'POST'])
def edit_password(id):
    user = db.session.query(User).filter_by(id=id).first()
    form = PasswordUpdateForm(request.form)
    if request.method == 'POST':
        if form.validate():
            user.password = generate_password_hash(form.password.data)
            db.session.add(user)
            db.session.commit()

            return redirect(url_for('users.edit_info', id=id))

    return render_template(current_app.config['TEMPLATE_THEME'] + '/users/edit_password.html', user=user, form=form)


@users.route('/<id>/edit', methods=['GET', 'POST'])
def edit_profile(id):
    user = User.query.filter_by(id=session['user_id']).first()
    form = UpdateForm(request.form)
    if request.method == 'POST':
        user.name = form.name.data
        user.homepage = form.homepage.data

        if request.form['sex_check'] == '1':
            user.sex = 'M'
        else:
            user.sex = 'F'

        if user.avatar != request.form.get('profileFileName'):
            s3 = boto3.resource('s3')
            s3.Object('static.inotone.co.kr', 'data/user/%s' % user.avatar).delete()
            user.avatar = request.form.get('profileFileName')

        if user.cover != request.form.get('coverFileName'):
            s3 = boto3.resource('s3')
            s3.Object('static.inotone.co.kr', 'data/cover/%s' % user.cover).delete()
            user.cover = request.form.get('coverFileName')

        db.session.add(user)
        db.session.commit()
        return redirect(url_for('users.edit_profile', id=id))
    return render_template(current_app.config['TEMPLATE_THEME'] + '/users/edit_profile.html', user=user, form=form)


@users.route('/profile_upload', methods=['POST'])
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
def profile_unload():
    if request.form.get('pre_file_name') != request.form.get('file_name'):
        s3 = boto3.resource('s3')
        s3.Object('static.inotone.co.kr', 'data/user/%s' % request.form.get('file_name')).delete()

    return jsonify({
        'file_name': request.form.get('file_name')
    })


@users.route('/cover_upload', methods=['POST'])
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
def cover_unload():
    if request.form.get('pre_file_name') != request.form.get('file_name'):
        s3 = boto3.resource('s3')
        s3.Object('static.inotone.co.kr', 'data/cover/%s' % request.form.get('file_name')).delete()

    return jsonify({
        'file_name': request.form.get('file_name')
    })


@users.route('/following', methods=['POST'])
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
