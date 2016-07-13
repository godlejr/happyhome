import os

import boto3
import shortuuid
from happyathome.models import db, Photo, File, Comment, PhotoComment, Magazine, MagazinePhoto, Room
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
        photo.file = file
        photo.user_id = '1'
        photo.room_id = request.form['room_id']
        photo.content = request.form['content']

        db.session.add(photo)
        db.session.commit()

        return redirect(url_for('photos.list'))

    rooms = db.session.query(Room).all()
    return render_template(current_app.config['TEMPLATE_THEME'] + '/photos/edit.html', rooms=rooms)


@photos.route('/<id>')
def detail(id):
    sub_photos = []
    vr_photos = []
    photo = db.session.query(Photo)
    post = photo.filter(Photo.id == id).first()
    if len(post.magazines):
        magazines = photo.filter(Photo.magazines.any(magazine_id=post.magazines[0].magazine_id))
        vr_photos = magazines.filter(Photo.file.has(type=2)).all()
        sub_photos = magazines.filter(Photo.file.has(type=1)).all()
    return render_template(current_app.config['TEMPLATE_THEME'] + '/photos/detail.html', post=post, sub_photos=sub_photos, vr_photos=vr_photos)


@photos.route('/<id>/comments/new', methods=['POST'])
def comment_new(id):
    if request.method == 'POST':
        comment = Comment()
        comment.user_id = '1'
        comment.content = request.form['comment']

        photo_comment = PhotoComment()
        photo_comment.photo_id = id
        photo_comment.comment = comment

        db.session.add(photo_comment)
        db.session.commit()
    return redirect(url_for('photos.detail', id=id))
