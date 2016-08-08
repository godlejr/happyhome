import base64
import os
import boto3
import html2text
import shortuuid
from flask import Blueprint, render_template, request, redirect, jsonify, url_for, current_app, session
from flask_login import login_required
from happyathome.forms import Pagination
from happyathome.models import db, File, Magazine, Comment, MagazineComment, Category, Residence, Photo, Room, User, \
    del_or_create, MagazineLike, MagazineScrap
from werkzeug.utils import secure_filename

magazines = Blueprint('magazines', __name__)


@magazines.context_processor
def utility_processor():
    def url_for_s3(s3path, filename=''):
        return ''.join((current_app.config['S3_BUCKET_NAME'], current_app.config[s3path], filename))
    return dict(url_for_s3=url_for_s3)


@magazines.context_processor
def utility_processor():
    def url_for_s3(s3path, filename=''):
        return ''.join((current_app.config['S3_BUCKET_NAME'], current_app.config[s3path], filename))
    return dict(url_for_s3=url_for_s3)


@magazines.route('/', defaults={'page': 1})
@magazines.route('/page/<int:page>')
def list(page):
    cards = db.session.query(Magazine)
    media = request.args.get('media', '')
    category_id = request.args.get('category_id', '')
    residence_id = request.args.get('residence_id', '')

    if media:
        cards = cards.filter(Magazine.photos.any(Photo.file.has(type=media)))
    if category_id:
        cards = cards.filter(Magazine.category_id == category_id)
    if residence_id:
        cards = cards.filter(Magazine.residence_id == residence_id)

    pagination = Pagination(page, 12, cards.count())
    if page != 1:
        offset = 12 * (page - 1)
    else:
        offset = 0

    cards = cards.order_by(Magazine.id.desc()).limit(12).offset(offset).all()
    categories = db.session.query(Category).all()
    residences = db.session.query(Residence).all()

    return render_template(current_app.config['TEMPLATE_THEME'] + '/magazines/list.html',
                           cards=cards,
                           media=media,
                           categories=categories,
                           residences=residences,
                           category_id=category_id,
                           residence_id=residence_id, pagination=pagination)


@magazines.route('/<id>')
def detail(id):
    post = db.session.query(Magazine).filter_by(id=id).first()
    post.hits += 1
    db.session.commit()

    comments = Comment.query.filter(Comment.magazines.any(magazine_id=id)).order_by(Comment.group_id.desc()).order_by(Comment.depth.asc()).all()
    return render_template(current_app.config['TEMPLATE_THEME'] + '/magazines/detail.html', post=post, comments=comments)


@magazines.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    categories = Category.query.all()
    residences = Residence.query.all()
    rooms = Room.query.all()
    if request.method == 'POST':
        h = html2text.HTML2Text()
        h.ignore_links = True
        h.ignore_images = True
        h.ignore_emphasis = True

        magazine = Magazine()
        magazine.user_id = session['user_id']
        magazine.category_id = request.form['category_id']
        magazine.residence_id = request.form['residence_id']
        magazine.title = request.form['title']
        magazine.size = request.form['size']
        magazine.location = request.form['location']
        magazine.cost = request.form['cost']
        magazine.content = request.form['content']
        magazine.content_txt = h.handle(request.form['content'])

        photo_files = request.files.getlist('photo_file')

        for idx, photo_file in enumerate(photo_files):
            photo_blob = photo_file.read()
            photo_name = secure_filename(''.join((shortuuid.uuid(), os.path.splitext(photo_file.filename)[1])))

            s3 = boto3.resource('s3')
            s3.Object('static.inotone.co.kr', 'data/img/%s' % photo_name).put(Body=photo_blob,
                                                                              ContentType=photo_file.content_type)

            file = File()
            file.type = 1
            file.name = photo_name
            file.ext = photo_name.split('.')[1]
            file.size = len(photo_blob)

            photo = Photo()
            photo.file = file
            photo.user_id = session['user_id']
            photo.room_id = request.form.getlist('room_id')[idx]
            photo.content = request.form.getlist('photo_content')[idx]

            magazine.photos.append(photo)
        db.session.add(magazine)
        db.session.commit()
        return redirect(url_for('magazines.list'))
    return render_template(current_app.config['TEMPLATE_THEME'] + '/magazines/new.html',
                           categories=categories,
                           residences=residences,
                           rooms=rooms)


@magazines.route('/<id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    magazine = Magazine.query.filter_by(user_id=session['user_id'], id=id).first()
    categories = Category.query.all()
    residences = Residence.query.all()
    rooms = Room.query.all()
    if request.method == 'POST':
        h = html2text.HTML2Text()
        h.ignore_links = True
        h.ignore_images = True
        h.ignore_emphasis = True

        magazine.user_id = session['user_id']
        magazine.category_id = request.form['category_id']
        magazine.residence_id = request.form['residence_id']
        magazine.title = request.form['title']
        magazine.size = request.form['size']
        magazine.location = request.form['location']
        magazine.cost = request.form['cost']
        magazine.content = request.form['content']
        magazine.content_txt = h.handle(request.form['content'])

        Photo.query.filter_by(user_id=session['user_id'], magazine_id=magazine.id).delete()

        photo_files = request.form.getlist('file_src')
        for idx, photo_file in enumerate(photo_files):
            photo_blob = base64.b64decode(photo_file.split(',')[1])
            photo_name = secure_filename(''.join((shortuuid.uuid(), '.jpg')))

            s3 = boto3.resource('s3')
            s3.Object('static.inotone.co.kr', 'data/img/%s' % photo_name).put(Body=photo_blob,
                                                                              ContentType='image/jpeg')

            file = File()
            file.type = 1
            file.name = photo_name
            file.ext = 'jpg'
            file.size = len(photo_blob)

            photo = Photo()
            photo.file = file
            photo.user_id = session['user_id']
            photo.room_id = request.form.getlist('room_id')[idx]
            photo.content = request.form.getlist('photo_content')[idx]

            magazine.photos.append(photo)
        db.session.add(magazine)
        db.session.commit()
        return redirect(url_for('magazines.detail', id=id))
    return render_template(current_app.config['TEMPLATE_THEME'] + '/magazines/edit.html',
                           categories=categories,
                           residences=residences,
                           rooms=rooms,
                           magazine=magazine)


@magazines.route('/like', methods=['GET', 'POST'])
@login_required
def like():
    magazine_id = request.form.get('magazine_id', '')
    if request.method == 'POST':
        del_or_create(db.session, MagazineLike, user_id=session['user_id'], magazine_id=magazine_id)
    return jsonify({
        'magazine_id': magazine_id,
        'count': MagazineLike.query.filter_by(magazine_id=magazine_id).count()
    })


@magazines.route('/scrap', methods=['GET', 'POST'])
@login_required
def scrap():
    magazine_id = request.form.get('magazine_id', '')
    if request.method == 'POST':
        del_or_create(db.session, MagazineScrap, user_id=session['user_id'], magazine_id=magazine_id)
    return jsonify({
        'magazine_id': magazine_id,
        'count': MagazineScrap.query.filter_by(magazine_id=magazine_id).count()
    })


@magazines.route('/<id>/comments/new', methods=['GET', 'POST'])
@login_required
def comment_new(id):
    if request.method == 'POST':
        comment = Comment()
        comment.user_id = session['user_id']
        comment.group_id = comment.max1_group_id
        comment.content = request.form['comment']
        db.session.add(comment)
        db.session.commit()

        magazine_comment = MagazineComment()
        magazine_comment.magazine_id = id
        magazine_comment.comment_id = comment.id

        db.session.add(magazine_comment)
        db.session.commit()
    return redirect(url_for('magazines.detail', id=id))


@magazines.route('/comment_reply', methods=['POST'])
def comment_reply():
    if request.method == 'POST':
        comment = Comment()
        comment.user_id = session['user_id']
        comment.group_id = request.form.get('group_id')
        comment.content = request.form.get('content')
        comment.depth = 1
        db.session.add(comment)
        db.session.commit()

        magazine_comment = MagazineComment()
        magazine_comment.magazine_id = request.form.get('magazine_id')
        magazine_comment.comment_id = comment.id

        db.session.add(magazine_comment)
        db.session.commit()

        user = db.session.query(User).filter(User.id == session['user_id']).first();

        return jsonify({
            'comment_id':comment.id,
            'user_id':session['user_id'],
            'user_name':user.name,
            'created_date':comment.created_date,
            'comment': comment.content,
            'group_id': comment.get_parent_id(comment.group_id),
            'avatar': user.avatar
        })


@magazines.route('/comment_edit', methods=['POST'])
def comment_edit():
    if request.method == 'POST':
        comment = db.session.query(Comment).filter(Comment.id == request.form.get('comment_id')).first()
        comment.content = request.form.get('content')

        db.session.add(comment)
        db.session.commit()

        return jsonify({
            'comment': comment.content
        })


@magazines.route('/comment_remove', methods=['POST'])
def comment_remove():
    if request.method == 'POST':
        db.session.query(Comment).filter(Comment.id == request.form.get('comment_id')).update({ 'deleted' : True })
        db.session.commit()

        return jsonify({
            'ok': 1
        })


@magazines.route('/<id>/delete')
@login_required
def delete(id):
    db.session.query(Comment).filter(Comment.magazines.any(Magazine.id == id)).delete(synchronize_session=False)
    magazine = db.session.query(Magazine).filter_by(id=id)
    photos = db.session.query(Photo).filter(Photo.magazine_id == id).all()

    for photo in photos:
        s3 = boto3.resource('s3')
        s3.Object('static.inotone.co.kr', 'data/img/%s' % photo.file.name).delete()

    magazine.delete()
    db.session.commit()

    return redirect(url_for('magazines.list'))


