import os

import boto3
import shortuuid
from happyathome.models import db, Interior, Photo
from flask import Blueprint, render_template, request, redirect, url_for, abort
from werkzeug.utils import secure_filename

TEMPLATE = 'bootstrap'
interior = Blueprint('interior', __name__)


@interior.route('')
def list():
    posts = db.session.query(Interior).order_by(Interior.id.desc()).all()
    return render_template(TEMPLATE + '/interior/list.html', posts=posts)


@interior.route('/new', methods=['GET','POST'])
def new():
    if request.method == 'POST':
        file = request.files['photo']
        file_blob = file.read()
        file_name = secure_filename(''.join((shortuuid.uuid(), os.path.splitext(file.filename)[1])))

        s3 = boto3.resource('s3')
        s3.Object('static.inotone.co.kr', 'data/img/%s' % file_name).put(Body=file_blob, ContentType=file.content_type)

        photo = Photo()
        photo.filename = file_name
        photo.filesize = len(file_blob)

        post = Interior()
        post.user_id = '1'
        post.photos = photo
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.add(post)
        db.session.commit()

        return redirect(url_for('interior.list'))
    return render_template(TEMPLATE + '/interior/edit.html')


@interior.route('/<interior_id>')
def detail(interior_id):
    try:
        post = db.session.query(Interior).filter_by(id=interior_id).first()
        posts = db.session.query(Interior) \
            .filter(Interior.user_id == post.user_id) \
            .filter(Interior.id != post.id) \
            .order_by(Interior.id.desc()) \
            .all()
        return render_template(TEMPLATE + '/interior/detail.html', post=post, posts=posts)
    except Exception as e:
        print(e)
        abort(404)
