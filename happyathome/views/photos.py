import os

import boto3
import shortuuid
from happyathome.models import db, Photo, File
from flask import Blueprint, render_template, request, redirect, url_for, abort, current_app
from werkzeug.utils import secure_filename

photos = Blueprint('photos', __name__)


@photos.route('')
def list():
    posts = db.session.query(Photo).order_by(Photo.id.desc()).all()
    return render_template(current_app.config['TEMPLATE_THEME'] + '/photos/list.html', posts=posts)


@photos.route('/new', methods=['GET','POST'])
def new():
    if request.method == 'POST':
        file = request.files['photo_file']
        file_blob = file.read()
        file_name = secure_filename(''.join((shortuuid.uuid(), os.path.splitext(file.filename)[1])))

        s3 = boto3.resource('s3')
        s3.Object('static.inotone.co.kr', 'data/img/%s' % file_name).put(Body=file_blob, ContentType=file.content_type)

        file = File()
        file.name = file_name
        file.size = len(file_blob)

        post = Photo()
        post.user_id = '1'
        post.files = file
        post.content = request.form['content']

        db.session.add(post)
        db.session.commit()

        return redirect(url_for('photos.list'))
    return render_template(current_app.config['TEMPLATE_THEME'] + '/photos/edit.html')


@photos.route('/<id>')
def detail(id):
    post = db.session.query(Photo).filter_by(id=id).first()
    return render_template(current_app.config['TEMPLATE_THEME'] + '/photos/detail.html', post=post)

