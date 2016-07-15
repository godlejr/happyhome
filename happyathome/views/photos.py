import os
import boto3
import shortuuid
from flask_login import login_required
from happyathome.models import db, Photo, File, Comment, PhotoComment, Room
from flask import Blueprint, render_template, request, redirect, url_for, current_app
from werkzeug.utils import secure_filename

photos = Blueprint('photos', __name__)


@photos.route('/')
def list():
    posts = db.session.query(Photo)
    room_id = request.args.get('room_id') or ''
    if room_id:
        posts = posts.filter(Photo.room_id == room_id)
    posts = posts.order_by(Photo.id.desc()).all()
    rooms = db.session.query(Room).all()
    return render_template(current_app.config['TEMPLATE_THEME'] + '/photos/list.html', posts=posts, rooms=rooms, room_id=room_id)


@photos.route('/<id>')
def detail(id):
    magazine_photos = []
    magazine_vrs = []
    room_photos = []
    photo = db.session.query(Photo)
    post = photo.filter(Photo.id == id).first()
    others = photo.filter(Photo.id != id).filter(Photo.file.has(type=1))
    user_photos = others.filter(Photo.user_id == post.user_id).order_by(Photo.id.desc()).limit(6).all()
    if post.room_id:
        room_photos = others.filter(Photo.room_id == post.room_id).order_by(Photo.id.desc()).limit(6).all()
    if post.magazine_id:
        magazine = photo.filter(Photo.magazine_id == post.magazine_id)
        magazine_vrs = magazine.filter(Photo.file.has(type=2)).all()
        magazine_photos = magazine.filter(Photo.file.has(type=1)).all()
    return render_template(current_app.config['TEMPLATE_THEME'] + '/photos/detail.html',
                           post=post,
                           room_photos=room_photos,
                           user_photos=user_photos,
                           magazine_vrs=magazine_vrs,
                           magazine_photos=magazine_photos)


@photos.route('/new', methods=['GET', 'POST'])
@login_required
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


@photos.route('/<id>/comments/new', methods=['POST'])
@login_required
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
