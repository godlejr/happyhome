import os

import boto3
import shortuuid
from happyathome.models import db, Snapshot, Photo
from flask import Blueprint, render_template, request, redirect, url_for, abort
from werkzeug.utils import secure_filename

TEMPLATE = 'bootstrap'
snapshot = Blueprint('snapshot', __name__)


@snapshot.route('')
def list():
    posts = db.session.query(Snapshot).order_by(Snapshot.id.desc()).all()
    return render_template(TEMPLATE + '/snapshot/list.html', posts=posts)


@snapshot.route('/new', methods=['GET','POST'])
def new():
    if request.method == 'POST':
        file = request.files['photo']
        file_blob = file.read()
        file_name = secure_filename(''.join((shortuuid.uuid(), os.path.splitext(file.filename)[1])))

        s3 = boto3.resource('s3')
        s3.Object('s3.inotone.co.kr', 'data/img/%s' % file_name).put(Body=file_blob, ContentType=file.content_type)

        photo = Photo()
        photo.filename = file_name
        photo.filesize = len(file_blob)

        post = Snapshot()
        post.user_id = '1'
        post.photos = photo
        post.content = request.form['content']
        db.session.add(post)
        db.session.commit()

        return redirect(url_for('snapshot.list'))
    return render_template(TEMPLATE + '/snapshot/edit.html')


@snapshot.route('/<snapshot_id>')
def detail(snapshot_id):
    try:
        post = db.session.query(Snapshot).filter_by(id=snapshot_id).first()
        posts = db.session.query(Snapshot) \
            .filter(Snapshot.user_id == post.user_id) \
            .filter(Snapshot.id != post.id) \
            .order_by(Snapshot.id.desc()) \
            .all()
        return render_template(TEMPLATE + '/snapshot/detail.html', post=post, posts=posts)
    except:
        abort(404)
