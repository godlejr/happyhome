import base64
import os
import boto3
import httplib2
import shortuuid
from flask import session
from flask_login import login_required, current_user
from googleapiclient import discovery
from googleapiclient.http import MediaFileUpload
from happyathome.forms import Pagination
from happyathome.lib import youtube_api
from happyathome.lib.youtube_api import initialize_upload, resumable_upload
from happyathome.models import db, del_or_create, Photo, File, Comment, PhotoComment, Room, PhotoLike, PhotoScrap, User, \
    Magazine
from flask import Blueprint, render_template, request, redirect, url_for, current_app, jsonify
from oauth2client import client
from oauth2client import service_account
from oauth2client.file import Storage
from sqlalchemy import func
from werkzeug.utils import secure_filename

photos = Blueprint('photos', __name__)


@photos.context_processor
def utility_processor():
    def url_for_s3(s3path, filename=''):
        return ''.join((current_app.config['S3_BUCKET_NAME'], current_app.config[s3path], filename))

    return dict(url_for_s3=url_for_s3)


@photos.route('/', defaults={'page': 1})
@photos.route('/page/<int:page>')
def list(page):
    col = request.args.get('col', 4)
    media = request.args.get('media', '')
    level = request.args.get('level', '')
    room_id = request.args.get('room_id', '')
    sort = request.args.get('sort', '')

    rooms = Room.query.all()
    cards = db.session.query(Photo)
    room = Room.query.filter_by(id=room_id).first()

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

    if sort == 'likes':
        cards = cards.outerjoin(PhotoLike). \
            group_by(Photo.id).order_by(func.count(PhotoLike.photo_id).desc()). \
            limit(12).offset(offset).all()
    elif sort == 'recent':
        cards = cards.order_by(Photo.id.desc()).limit(12).offset(offset).all()
    else:
        cards = cards.order_by(Photo.hits.desc()).limit(12).offset(offset).all()

    return render_template(current_app.config['TEMPLATE_THEME'] + '/gallery/list.html',
                           col=col,
                           room=room,
                           rooms=rooms,
                           cards=cards,
                           pagination=pagination,
                           query_string=request.query_string.decode('utf-8'))


@photos.route('/<id>')
def detail(id):
    magazine_photos = []
    post = db.session.query(Photo).filter(Photo.id == id).first()
    post.hits += 1
    db.session.commit()

    comments = Comment.query.filter(Comment.photos.any(photo_id=id)).order_by(Comment.group_id.desc(),
                                                                              Comment.depth.asc()).order_by().all()
    user_photos = db.session.query(Photo). \
        filter(Photo.id != id). \
        filter(Photo.user_id == post.user_id). \
        order_by(Photo.hits.desc()). \
        limit(8). \
        all()
    if post.magazine_id:
        magazine_photos = db.session.query(Photo).filter(Photo.magazine_id == post.magazine_id).all()

    return render_template(current_app.config['TEMPLATE_THEME'] + '/gallery/detail.html',
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
        photo_name = secure_filename(''.join((shortuuid.uuid(), os.path.splitext(request.form.get('file_name'))[1].lower())))

        s3 = boto3.resource('s3')
        s3.Object('static.inotone.co.kr', 'data/img/%s' % photo_name).put(Body=base64.b64decode(photo_data),
                                                                          ContentType='image/jpeg')

        return jsonify({
            'file_name': photo_name,
            'photo_data': photo_data
        })


@photos.route('/unload', methods=['POST'])
@login_required
def unload():
    if request.form.get('pre_file_name') != request.form.get('file_name'):
        s3 = boto3.resource('s3')
        s3.Object('static.inotone.co.kr', 'data/img/%s' % request.form.get('file_name')).delete()

    return jsonify({
        'file_name': request.form.get('file_name')
    })


@photos.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    photo = Photo()
    rooms = Room.query.all()
    if request.method == 'POST':
        file = File()

        if request.form['content_type'] == '3':
            photo_file = request.files['photo_file']
            photo_name = secure_filename(''.join((shortuuid.uuid(), os.path.splitext(photo_file.filename)[1].lower())))
            photo_path = os.path.join(current_app.config['UPLOAD_TMP_DIRECTORY'], photo_name)
            photo_file.save(photo_path)
            file.size = os.stat(photo_path).st_size
        else:
            photo_name = request.form['file_name']
            file.size = 0
        file.type = request.form['content_type']
        file.name = photo_name
        file.ext = photo_name.split('.')[1]

        photo.file = file
        photo.user_id = session['user_id']
        photo.room_id = request.form['room_id']
        photo.content = request.form['content']

        db.session.add(photo)
        db.session.flush()
        db.session.commit()

        if request.form['content_type'] == '3':
            body = dict(
                snippet=dict(
                    title='해피홈 갤러리 동영상 (%s)' % photo.id,
                    description=request.form['content']
                ),
                status=dict(
                    privacyStatus='public'
                )
            )

            youtube = youtube_api.auth_account()
            insert_request = youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=MediaFileUpload(photo_path, chunksize=-1, resumable=True)
            )

            data = resumable_upload(insert_request)
            if data.get('status') == '200':
                File.query.filter_by(id=file.id).update({'cid': data['response']['id']})
                db.session.commit()

        return redirect(url_for('photos.list'))
    return render_template(current_app.config['TEMPLATE_THEME'] + '/gallery/edit.html', rooms=rooms, photo=photo)


@photos.route('/<id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    photo = Photo.query.filter_by(id=id, user_id=current_user.id).first()
    rooms = Room.query.all()
    if request.method == 'POST':
        photo_name = request.form['file_name']

        if photo.is_youtube:
            youtube = youtube_api.auth_account()
            youtube.videos().delete(id=photo.file.cid).execute()
        else:
            if photo_name != photo.file.name:
                s3 = boto3.resource('s3')
                s3.Object('static.inotone.co.kr', 'data/img/%s' % photo.file.name).delete()

        if request.form['content_type'] == '3':
            photo_file = request.files['photo_file']
            photo_name = secure_filename(''.join((shortuuid.uuid(), os.path.splitext(photo_file.filename)[1].lower())))
            photo_path = os.path.join(current_app.config['UPLOAD_TMP_DIRECTORY'], photo_name)
            photo_file.save(photo_path)
            photo.file.size = os.stat(photo_path).st_size

            body = dict(
                snippet=dict(
                    title='해피홈 갤러리 동영상 (%s)' % photo.id,
                    description=request.form['content']
                ),
                status=dict(
                    privacyStatus='public'
                )
            )

            youtube = youtube_api.auth_account()
            insert_request = youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=MediaFileUpload(photo_path, chunksize=-1, resumable=True)
            )

            data = resumable_upload(insert_request)
            if data.get('status') == '200':
                photo.file.cid = data['response']['id']
            else:
                photo.file.cid = None
        else:
            photo.file.size = 0
            photo.file.cid = None

        photo.user_id = session['user_id']
        photo.room_id = request.form['room_id']
        photo.content = request.form['content']
        photo.file.type = request.form['content_type']
        photo.file.name = photo_name
        photo.file.ext = photo_name.split('.')[1]

        db.session.add(photo)
        db.session.commit()

        return redirect(url_for('photos.detail', id=id))
    return render_template(current_app.config['TEMPLATE_THEME'] + '/gallery/edit.html',
                           rooms=rooms,
                           photo=photo)


@photos.route('/<id>/delete')
@login_required
def delete(id):
    Comment.query.filter(Comment.photos.any(Photo.id == id)).delete(synchronize_session='fetch')
    photo = Photo.query.filter_by(id=id, user=current_user).first()
    photo_file = File.query.filter_by(id=photo.file_id).first()

    if photo.is_youtube:
        youtube = youtube_api.auth_account()
        youtube.videos().delete(id=photo.file.cid).execute()
    else:
        s3 = boto3.resource('s3')
        s3.Object('static.inotone.co.kr', 'data/img/%s' % photo.file.name).delete()

    db.session.delete(photo)
    db.session.delete(photo_file)
    db.session.commit()

    return redirect(url_for('photos.list'))


@photos.route('/<id>/comments/new', methods=['GET', 'POST'])
@login_required
def comment_new(id):
    if request.method == 'POST':
        if request.form['comment'] != "":
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
@login_required
def comment_reply():
    if request.method == 'POST':
        if request.form.get('content') != "":
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
                'comment_id': comment.id,
                'user_id': session['user_id'],
                'user_name': user.name,
                'created_date': comment.created_date,
                'comment': comment.content,
                'group_id': comment.get_parent_id(comment.group_id),
                'avatar': user.avatar
            })


@photos.route('/comment_edit', methods=['POST'])
@login_required
def comment_edit():
    if request.method == 'POST':
        if request.form.get('content') != "":
            comment = db.session.query(Comment).filter(Comment.id == request.form.get('comment_id')).first()
            comment.content = request.form.get('content')

            db.session.add(comment)
            db.session.commit()

            return jsonify({
                'comment': comment.content
            })


@photos.route('/comment_remove', methods=['POST'])
@login_required
def comment_remove():
    if request.method == 'POST':
        db.session.query(Comment).filter(Comment.id == request.form.get('comment_id')).update({'deleted': True})
        db.session.commit()

        return jsonify({
            'ok': 1
        })


@photos.route('/magazine_check', methods=['POST'])
@login_required
def magazine_check():
    if request.method == 'POST':
        photo = Photo.query.filter_by(id=request.form.get('photo_id')).first()

        if photo.magazine_id:
            magazine = Magazine.query.filter_by(id=photo.magazine_id).first();
            return jsonify({
                'check': 1,
                'magazine_name': magazine.title
            })

        return jsonify({
            'check': 2,
            'photo_id': request.form.get('photo_id')
        })
