import os

import boto3
import html2text
import shortuuid
from happyathome.models import db, Magazine, Photo, Interior
from flask import Blueprint, render_template, request, redirect, jsonify, url_for
from werkzeug.utils import secure_filename

TEMPLATE = 'bootstrap'
magazine = Blueprint('magazine', __name__)


@magazine.route('')
def list():
    magazines = db.session.query(Magazine).order_by(Magazine.id.desc()).all()
    return render_template(TEMPLATE + '/magazine/list.html', magazines=magazines)


@magazine.route('/image/upload', methods=['POST'])
def image_upload():
    file = request.files['imageUpload']
    file_blob = file.read()
    file_name = secure_filename(''.join((shortuuid.uuid(), os.path.splitext(file.filename)[1])))

    s3 = boto3.resource('s3')
    s3.Object('static.inotone.co.kr', 'data/img/%s' % file_name).put(Body=file_blob, ContentType=file.content_type)

    photo = Photo()
    photo.filename = file_name
    photo.filesize = len(file_blob)
    db.session.add(photo)
    db.session.commit()

    return jsonify({
        'status': '200',
        'message': 'Done',
        'url': '/static/data/sample.jpg'
    })


@magazine.route('/new', methods=['GET', 'POST'])
def new():
    if request.method == 'POST':
        h = html2text.HTML2Text()
        h.ignore_links = True
        h.ignore_images = True
        h.ignore_emphasis = True

        mz = Magazine()
        mz.user_id = '1'
        mz.title = request.form['title']
        mz.content = request.form['content']
        mz.content_txt = h.handle(request.form['content'])

        db.session.add(mz)
        db.session.commit()

        return redirect(url_for('magazine.list'))
    return render_template(TEMPLATE + '/magazine/edit.html')


@magazine.route('/<magazine_id>')
def detail(magazine_id):
    post = db.session.query(Magazine).filter_by(id=magazine_id).first()
    posts = db.session.query(Interior) \
        .filter(Interior.user_id == post.user_id) \
        .order_by(Interior.id.desc()) \
        .all()
    return render_template(TEMPLATE + '/magazine/detail.html', post=post, posts=posts)
