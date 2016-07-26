import os
import boto3
import html2text
import shortuuid
from flask import Blueprint, render_template, request, redirect, jsonify, url_for, current_app
from happyathome.forms import Pagination
from happyathome.models import db, File, Magazine, Comment, MagazineComment, Category, Residence, Photo, Room
from werkzeug.utils import secure_filename

magazines = Blueprint('magazines', __name__)


@magazines.route('/', defaults={'page': 1})
@magazines.route('/page/<int:page>')
def list(page):
    posts = db.session.query(Magazine)
    media = request.args.get('media') or ''
    category_id = request.args.get('category_id') or ''
    residence_id = request.args.get('residence_id') or ''

    if media:
        posts = posts.filter(Magazine.photos.any(Photo.file.has(type=media)))
    if category_id:
        posts = posts.filter(Magazine.category_id == category_id)
    if residence_id:
        posts = posts.filter(Magazine.residence_id == residence_id)

    pagination = Pagination(page, 12, posts.count())
    if page != 1:
        offset = 12 * (page - 1)
    else:
        offset = 0

    posts = posts.order_by(Magazine.id.desc()).limit(12).offset(offset).all()
    categories = db.session.query(Category).all()
    residences = db.session.query(Residence).all()

    return render_template(current_app.config['TEMPLATE_THEME'] + '/magazines/list.html',
                           posts=posts,
                           media=media,
                           categories=categories,
                           residences=residences,
                           category_id=category_id,
                           residence_id=residence_id, pagination=pagination)


@magazines.route('/new', methods=['GET', 'POST'])
def new():
    if request.method == 'POST':
        h = html2text.HTML2Text()
        h.ignore_links = True
        h.ignore_images = True
        h.ignore_emphasis = True

        magazine = Magazine()
        magazine.user_id = '1'
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
            photo.user_id = '1'
            photo.room_id = request.form.getlist('room_id')[idx]
            photo.content = request.form.getlist('photo_content')[idx]

            magazine.photos.append(photo)
        db.session.add(magazine)
        db.session.commit()

        return redirect(url_for('magazines.list'))

    categories = db.session.query(Category).all()
    residences = db.session.query(Residence).all()
    rooms = db.session.query(Room).all()
    return render_template(current_app.config['TEMPLATE_THEME'] + '/magazines/edit.html',
                           categories=categories,
                           residences=residences,
                           rooms=rooms)


@magazines.route('/<id>')
def detail(id):
    post = db.session.query(Magazine).filter_by(id=id).first()
    return render_template(current_app.config['TEMPLATE_THEME'] + '/magazines/detail.html', post=post)


@magazines.route('/<id>/comments/new', methods=['POST'])
def comment_new(id):
    if request.method == 'POST':
        comment = Comment()
        comment.user_id = '1'
        comment.content = request.form['comment']

        magazine_comment = MagazineComment()
        magazine_comment.magazine_id = id
        magazine_comment.comment = comment

        db.session.add(magazine_comment)
        db.session.commit()
    return redirect(url_for('magazines.detail', id=id))
