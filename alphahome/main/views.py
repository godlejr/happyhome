from flask import render_template, request, flash, redirect, url_for
from alphahome.forms import JoinForm
from alphahome.main import main
from alphahome.models import User, Post, Photo, db
from werkzeug import secure_filename

import os
import shortuuid

TEMPLATE = 'bootstrap'

@main.route('/')
def index():
    posts = db.session.query(Post.id,Post.title,Post.content,Photo.filename).join(Photo, Photo.post_id == Post.id).all()
    return render_template(TEMPLATE + '/main/index.html', posts=posts)


@main.route('/post/new', methods=['GET','POST'])
def post_new():
    if request.method == 'POST':
        post = Post()
        post.user_id = '1'
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.add(post)
        db.session.flush()

        file = request.files['photo']
        filename = secure_filename(file.filename)
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
    return render_template(TEMPLATE + '/main/post_edit.html')


@main.route('/post/<post_id>')
def post_detail(post_id):
    post = db.session.query(Post.id, Post.title, Post.content, Photo.filename)\
        .join(Photo, Photo.post_id == Post.id)\
        .filter(Post.id == post_id).first()
    return render_template(TEMPLATE + '/main/post_detail.html', post=post)


@main.route('/join', methods=['GET','POST'])
def join():
    form = JoinForm(request.form)
    if request.method == 'POST':
        if form.validate():
            user = User()
            user.email = form.email.data
            user.password = form.password.data
            db.session.add(user)
            db.session.commit()
            flash('가입을 축하합니다.')
            return redirect(url_for('main.user_list'))

    return render_template(TEMPLATE + '/main/join.html', form=form)


@main.route('/users')
def user_list():
    return render_template(TEMPLATE + '/main/user_list.html', users=User.query.all())
