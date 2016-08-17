import os
import boto3
import html2text
import shortuuid
from flask import Blueprint, render_template, request, redirect, jsonify, url_for, current_app, session
from flask_login import login_required, current_user
from happyathome.forms import Pagination
from happyathome.models import db, File, Magazine, Comment, MagazineComment, Category, Residence, Photo, Room, User, \
    del_or_create, MagazineLike, MagazineScrap
from sqlalchemy import func
from werkzeug.utils import secure_filename
from wtforms.validators import length

magazines = Blueprint('magazines', __name__)


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
    likes = request.args.get('likes', '')
    recent = request.args.get('recent', '')

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

    if likes:
        cards = cards.outerjoin(MagazineLike).group_by(Magazine.id).order_by(func.count(MagazineLike.magazine_id).desc()).limit(
            12).offset(offset).all()
    elif recent:
        cards = cards.order_by(Magazine.id.desc()).limit(12).offset(offset).all()
    else:
        cards = cards.order_by(Magazine.hits.desc()).limit(12).offset(offset).all()

    categories = db.session.query(Category).all()
    residences = db.session.query(Residence).all()

    return render_template(current_app.config['TEMPLATE_THEME'] + '/magazines/list.html',
                           cards=cards,
                           media=media,
                           categories=categories,
                           residences=residences,
                           category_id=category_id,
                           residence_id=residence_id,
                           pagination=pagination,
                           query_string=request.query_string.decode('utf-8'))


@magazines.route('/<id>')
def detail(id):
    post = db.session.query(Magazine).filter_by(id=id).first()
    post.hits += 1
    db.session.commit()

    comments = Comment.query.filter(Comment.magazines.any(magazine_id=id)).order_by(Comment.group_id.desc()).order_by(Comment.depth.asc()).all()
    category = Category.query.filter(Category.id == post.category_id).first()
    category_magazines = Magazine.query.filter(Magazine.category_id == category.id).filter(Magazine.id != post.id).limit(4).all()

    residence = Residence.query.filter(Residence.id == post.residence_id).first()
    residence_magazines = Magazine.query.filter(Magazine.residence_id == residence.id).filter(Magazine.id != post.id).limit(4).all()

    user = User.query.filter(User.id == post.user_id).first()
    user_magazines = Magazine.query.filter(Magazine.user_id == user.id ).filter(Magazine.id != post.id).limit(4).all()

    return render_template(current_app.config['TEMPLATE_THEME'] + '/magazines/detail.html', post=post,
                           comments=comments,
                           category_magazines=category_magazines, residence_magazines=residence_magazines,
                           user_magazines=user_magazines
                           )


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
    magazine = Magazine.query.filter_by(id=id, user_id=current_user.id).first()
    categories = Category.query.all()
    residences = Residence.query.all()
    rooms = Room.query.all()
    if request.method == 'POST':
        s3 = boto3.resource('s3')

        h = html2text.HTML2Text()
        h.ignore_links = True
        h.ignore_images = True
        h.ignore_emphasis = True

        magazine.user_id = current_user.id
        magazine.category_id = request.form['category_id']
        magazine.residence_id = request.form['residence_id']
        magazine.title = request.form['title']
        magazine.size = request.form['size']
        magazine.location = request.form['location']
        magazine.cost = request.form['cost']
        magazine.content = request.form['content']
        magazine.content_txt = h.handle(request.form['content'])

        photo_ids = request.form.getlist('photo_id')
        for idx, photo_id in enumerate(photo_ids):
            photo = Photo.query.filter_by(id=photo_id, magazine_id=id, user_id=current_user.id).first()
            if not photo:
                photo = Photo()
                photo.magazine_id = id
                photo.user_id = current_user.id
            photo.room_id = request.form.getlist('room_id')[idx]
            photo.content = request.form.getlist('photo_content')[idx]

            photo_file = request.files.getlist('photo_file')[idx]
            if photo_file:
                photo_blob = photo_file.read()
                photo_name = secure_filename(''.join((shortuuid.uuid(), '.jpg')))

                s3.Object('static.inotone.co.kr', 'data/img/%s' % photo_name).put(Body=photo_blob, ContentType='image/jpeg')
                if photo.file:
                    s3_file = s3.Object('static.inotone.co.kr', 'data/img/%s' % photo.file.name)
                    if s3_file:
                        s3_file.delete()

                file = File()
                file.type = 1
                file.name = photo_name
                file.ext = 'jpg'
                file.size = len(photo_blob)

                photo.file = file
            db.session.add(photo)
        db.session.commit()

        photo_delete_ids = request.form.getlist('photo_delete_id')
        for photo_delete_id in photo_delete_ids:
            photo = Photo.query.filter_by(id=photo_delete_id, user_id=current_user.id).first()
            s3_file = s3.Object('static.inotone.co.kr', 'data/img/%s' % photo.file.name)
            if s3_file:
                s3_file.delete()
            db.session.delete(photo)
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
        if request.form['comment'] != "":
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


@magazines.route('/comment_remove', methods=['POST'])
@login_required
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


