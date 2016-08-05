import base64
import os
import boto3
import shortuuid
from flask import session
from flask_login import login_required
from happyathome.forms import Pagination
from happyathome.models import db, del_or_create, Photo, File, Comment, PhotoComment, Room, PhotoLike, PhotoScrap, User
from flask import Blueprint, render_template, request, redirect, url_for, current_app, jsonify
from sqlalchemy import func
from werkzeug.utils import secure_filename

photos = Blueprint('photos', __name__)


@photos.route('/', defaults={'page': 1})
@photos.route('/page/<int:page>')
def list(page):
    media = request.args.get('media', '')
    level = request.args.get('level', '')
    room_id = request.args.get('room_id', '')
    rooms = db.session.query(Room).all()
    cards = db.session.query(Photo)

    if media:
        cards = cards.filter(Photo.file.has(type=media))
    if level:
        cards = cards.filter(Photo.user.has(level=level))
    if room_id:
        cards = cards.filter(Photo.room_id == room_id)

    pagination = Pagination(page, 12, cards.count())
    if page != 1:
        offset = 12 * (page - 1)
    else:
        offset = 0

    cards = cards.order_by(Photo.id.desc()).limit(12).offset(offset).all()

    return render_template(current_app.config['TEMPLATE_THEME'] + '/photos/list.html',
                           cards=cards,
                           rooms=rooms,
                           room_id=room_id,
                           pagination=pagination)


@photos.route('/<id>')
def detail(id):
    magazine_photos = []
    post = db.session.query(Photo).filter(Photo.id == id).first()
    post.hits += 1
    db.session.commit()

    comments = Comment.query.filter(Comment.photos.any(photo_id=id)).order_by(Comment.group_id.desc()).order_by(
        Comment.depth.asc()).all()
    user_photos = db.session.query(Photo). \
        filter(Photo.id != id). \
        filter(Photo.user_id == post.user_id). \
        order_by(Photo.id.desc()). \
        limit(6). \
        all()
    if post.magazine_id:
        magazine_photos = db.session.query(Photo).filter(Photo.magazine_id == post.magazine_id).all()

    return render_template(current_app.config['TEMPLATE_THEME'] + '/photos/detail.html',
                           post=post,
                           user_photos=user_photos,
                           magazine_photos=magazine_photos,
                           request_url=request.url,
                           comments=comments)


@photos.route('/upload', methods=['POST'])
@login_required
def upload():
    if request.method == "POST":
        photo_data = request.form.get('file_data').split(',')[1]
        photo_name = secure_filename(''.join((shortuuid.uuid(), os.path.splitext(request.form.get('file_name'))[1])))

        file = File()
        file.type = 1
        file.name = photo_name
        file.ext = photo_name.split('.')[1]
        file.size = (len(photo_data) * 3) / 4

        db.session.add(file)
        db.session.flush()
        db.session.commit()

        s3 = boto3.resource('s3')
        s3.Object('static.inotone.co.kr', 'data/img/%s' % photo_name).put(Body=base64.b64decode(photo_data), ContentType='image/jpeg')

        return jsonify({
            'file_id': file.id,
            'file_name': photo_name
        })


@photos.route('/unload', methods=['POST'])
@login_required
def unload():
    s3 = boto3.resource('s3')
    s3.Object('static.inotone.co.kr', 'data/img/%s' % request.form.get('file_name')).delete()
    return jsonify({
        'file_name': request.form.get('file_name')
    })


@photos.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'POST':
        if request.form.getlist('content_type'):
            db.session.query(File).filter_by(id=request.form['file_id']).update({'type': '2'})

        photo = Photo()
        photo.user_id = session['user_id']
        photo.file_id = request.form['file_id']
        photo.room_id = request.form['room_id']
        photo.content = request.form['content']

        db.session.add(photo)
        db.session.commit()

        return redirect(url_for('photos.list'))

    rooms = db.session.query(Room).all()
    return render_template(current_app.config['TEMPLATE_THEME'] + '/photos/edit.html', rooms=rooms)


@photos.route('/<id>/comments/new', methods=['GET', 'POST'])
@login_required
def comment_new(id):
    if request.method == 'POST':

        comment = Comment()
        comment.group_id = comment.max1_group_id
        comment.user_id = session['user_id']
        comment.content = request.form['comment']

        db.session.add(comment)
        db.session.commit()

        photo_comment = PhotoComment()
        photo_comment.photo_id = id
        photo_comment.comment_id = comment.id

        db.session.add(photo_comment)
        db.session.commit()
    return redirect(url_for('photos.detail', id=id))


@photos.route('/like', methods=['GET', 'POST'])
@login_required
def like():
    photo_id = request.form.get('photo_id', '')
    if request.method == 'POST':
        del_or_create(db.session, PhotoLike, user_id=session['user_id'], photo_id=photo_id)
    return jsonify({
        'photo_id': photo_id,
        'count': PhotoLike.query.filter_by(photo_id=photo_id).count()
    })


@photos.route('/scrap', methods=['GET', 'POST'])
@login_required
def scrap():
    photo_id = request.form.get('photo_id', '')
    if request.method == 'POST':
        del_or_create(db.session, PhotoScrap, user_id=session['user_id'], photo_id=photo_id)
    return jsonify({
        'photo_id': photo_id,
        'count': PhotoScrap.query.filter_by(photo_id=photo_id).count()
    })


@photos.route('/comment_reply', methods=['POST'])
def comment_reply():
    if request.method == 'POST':
        comment = Comment()
        comment.user_id = session['user_id']
        comment.group_id = request.form.get('group_id')
        comment.content = request.form.get('content')
        comment.depth = 1
        db.session.add(comment)
        db.session.commit()

        photo_comment = PhotoComment()
        photo_comment.photo_id = request.form.get('photo_id')
        photo_comment.comment_id = comment.id

        db.session.add(photo_comment)
        db.session.commit()

        user = db.session.query(User).filter(User.id == session['user_id']).first();

        return jsonify({
            'comment_id':comment.id,
            'user_id':session['user_id'],
            'user_name':user.name,
            'created_date':comment.created_date,
            'comment': comment.content,
            'group_id': comment.get_parent_id(comment.group_id)
        })


@photos.route('/comment_edit', methods=['POST'])
def comment_edit():
    if request.method == 'POST':
        comment = db.session.query(Comment).filter(Comment.id == request.form.get('comment_id')).first()
        comment.content = request.form.get('content')

        db.session.add(comment)
        db.session.commit()

        return jsonify({
            'comment': comment.content
        })


@photos.route('/comment_remove', methods=['POST'])
def comment_remove():
    if request.method == 'POST':
        db.session.query(Comment).filter(Comment.id == request.form.get('comment_id')).update({ 'deleted' : True })
        db.session.commit()

        return jsonify({
            'ok': 1
        })
