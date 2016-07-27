import base64
import os

import boto3
import shortuuid

from flask import Blueprint, render_template, request, redirect, url_for, current_app, jsonify
from happyathome.forms import Pagination, UpdateForm, PasswordUpdateForm, ProfessionalUpdateForm
from happyathome.models import db, User, Photo, Magazine, Professional, PhotoComment, Comment
from sqlalchemy import text
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

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


@users.route('/detail_qna/<id>')
def detail_qna(id):
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

    return render_template(current_app.config['TEMPLATE_THEME'] + '/users/detail_qna.html',
                           post=post,
                           photo_comments=photo_comments,
                           photo_comments_count=photo_comments_count,
                           magazine_comments=magazine_comments,
                           magazine_comments_count=magazine_comments_count,
                           current_app=current_app)



@users.route('/edit_professional/<id>', methods=['GET', 'POST'])
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

    return render_template(current_app.config['TEMPLATE_THEME'] + '/users/edit_professional.html', post=post, form=form)


@users.route('/edit_password/<id>', methods=['GET', 'POST'])
def edit_password(id):
    post = db.session.query(User).filter_by(id=id).first()
    form = PasswordUpdateForm(request.form)
    if request.method == 'POST':
        if form.validate():
            post.password = generate_password_hash(form.password.data)
            db.session.add(post)
            db.session.commit()

            return redirect(url_for('users.edit_info', id=id))

    return render_template(current_app.config['TEMPLATE_THEME'] + '/users/edit_password.html', post=post, form=form)


@users.route('/edit_info/<id>', methods=['GET', 'POST'])
def edit_info(id):
    post = db.session.query(User).filter_by(id=id).first()
    form = UpdateForm(request.form)
    if request.method == 'POST':
        post.name = form.name.data
        post.homepage = form.homepage.data

        if request.form['sex_check'] == '1':
            post.sex = 'M'
        else:
            post.sex = 'F'
        if post.avatar != request.form.get('profileFileName'):
            s3 = boto3.resource('s3')
            s3.Object('static.inotone.co.kr', 'data/user/%s' % post.avatar).delete()
            post.avatar = request.form.get('profileFileName')

        if post.cover != request.form.get('coverFileName'):
            s3 = boto3.resource('s3')
            s3.Object('static.inotone.co.kr', 'data/cover/%s' % post.cover).delete()
            post.cover = request.form.get('coverFileName')

        db.session.add(post)
        db.session.commit()
        return redirect(url_for('users.edit_info', id=id))

    return render_template(current_app.config['TEMPLATE_THEME'] + '/users/edit_info.html', post=post, form=form)


@users.route('/profile_upload', methods=['POST'])
def profile_upload():
    if request.method == "POST":
        photo_data = request.form.get('file_data').split(',')[1]
        photo_name = secure_filename(''.join((shortuuid.uuid(), os.path.splitext(request.form.get('file_name'))[1])))

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
        photo_name = secure_filename(''.join((shortuuid.uuid(), os.path.splitext(request.form.get('file_name'))[1])))

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
