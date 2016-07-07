import os

import boto3
import html2text
import shortuuid
from happyathome.models import db, Magazine, Photo, File
from flask import Blueprint, render_template, request, redirect, jsonify, url_for, current_app
from werkzeug.utils import secure_filename

magazines = Blueprint('magazines', __name__)


@magazines.route('')
def list():
    posts = db.session.query(Magazine).order_by(Magazine.id.desc()).all()
    return render_template(current_app.config['TEMPLATE_THEME'] + '/magazines/list.html', posts=posts)


@magazines.route('/image/upload', methods=['POST'])
def image_upload():
    file = request.files['imageUpload']
    file_blob = file.read()
    file_name = secure_filename(''.join((shortuuid.uuid(), os.path.splitext(file.filename)[1])))

    s3 = boto3.resource('s3')
    s3.Object('static.inotone.co.kr', 'data/img/%s' % file_name).put(Body=file_blob, ContentType=file.content_type)

    file = File()
    file.name = file_name
    file.size = len(file_blob)

    db.session.add(file)
    db.session.commit()

    return jsonify({
        'status': '200',
        'message': 'Done',
        'url': 'https://static.inotone.co.kr/data/img/%s' % file_name
    })


@magazines.route('/new', methods=['GET', 'POST'])
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
    return render_template(current_app.config['TEMPLATE_THEME'] + '/magazines/edit.html')


@magazines.route('/<id>')
def detail(id):
    post = db.session.query(Magazine).filter_by(id=id).first()
    posts = db.session.query(Magazine) \
        .filter(Magazine.user_id == post.user_id) \
        .order_by(Magazine.id.desc()) \
        .all()
    return render_template(current_app.config['TEMPLATE_THEME'] + '/magazines/detail.html', post=post, posts=posts)