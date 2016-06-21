import os

import werkzeug
from alphahome.models import Post, Photo, db
from flask import Blueprint, render_template, request, redirect

TEMPLATE = 'bootstrap'
snapshot = Blueprint('snapshot', __name__)


@snapshot.route('')
def list():
    posts = db.session.query(Post.id, Post.title, Post.content, Photo.filename).join(Photo, Photo.post_id == Post.id).all()
    return render_template(TEMPLATE + '/snapshot/list.html', posts=posts)


@snapshot.route('/new', methods=['GET','POST'])
def new():
    if request.method == 'POST':
        post = Post()
        post.user_id = '1'
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.add(post)
        db.session.flush()

        file = request.files['photo']
        filename = werkzeug.secure_filename(file.filename)
        filepath = os.path.join('/data/alphahome', filename)
        print(filepath)
        file.save(filepath)

        photo = Photo()
        photo.post_id = post.id
        photo.filename = filename
        photo.filesize = 0
        db.session.add(photo)
        db.session.commit()

        return redirect('/')
    return render_template(TEMPLATE + '/snapshot/edit.html')


@snapshot.route('/<post_id>')
def detail(post_id):
    post = db.session.query(Post.id, Post.title, Post.content, Photo.filename)\
        .join(Photo, Photo.post_id == Post.id)\
        .filter(Post.id == post_id).first()
    return render_template(TEMPLATE + '/snapshot/detail.html', post=post)
