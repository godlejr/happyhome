import os

import boto3
import shortuuid
from happyathome.models import db, Photo, File, Comment, PhotoComment
from flask import Blueprint, render_template, request, redirect, url_for, current_app
from werkzeug.utils import secure_filename

photos = Blueprint('photos', __name__)


@photos.route('')
def list():
    posts = db.session.query(Photo).order_by(Photo.id.desc()).all()
    return render_template(current_app.config['TEMPLATE_THEME'] + '/photos/list.html', posts=posts)


@photos.route('/new', methods=['GET', 'POST'])
def new():
    if request.method == 'POST':
        photo_file = request.files['photo_file']
        photo_blob = photo_file.read()
        photo_name = secure_filename(''.join((shortuuid.uuid(), os.path.splitext(photo_file.filename)[1])))

        s3 = boto3.resource('s3')
        s3.Object('static.inotone.co.kr', 'data/img/%s' % photo_name).put(Body=photo_blob, ContentType=photo_file.content_type)

        file = File()
        file.type = 1
        file.name = photo_name
        file.ext = photo_name.split('.')[1]
        file.size = len(photo_blob)

        photo = Photo()
        photo.user_id = '1'
        photo.file = file
        photo.content = request.form['content']

        db.session.add(photo)
        db.session.commit()

        return redirect(url_for('photos.list'))
    return render_template(current_app.config['TEMPLATE_THEME'] + '/photos/edit.html')


@photos.route('/<id>')
def detail(id):
    post = db.session.query(Photo).filter_by(id=id).first()
    return render_template(current_app.config['TEMPLATE_THEME'] + '/photos/detail.html', post=post)


@photos.route('/<id>/comments/new', methods=['POST'])
def comment_new(id):
    if request.method == 'POST':
        comment = Comment()
        comment.user_id = '1'
        comment.type = request.form['type']
        comment.content = request.form['comment']

        photo_comment = PhotoComment()
        photo_comment.photo_id = id
        photo_comment.comment = comment

        db.session.add(photo_comment)
        db.session.commit()
    return redirect(url_for('photos.detail', id=id))
