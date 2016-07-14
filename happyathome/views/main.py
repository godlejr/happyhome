from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, session, message_flashed
from happyathome.forms import JoinForm, LoginForm
from happyathome.models import db, User, Magazine, Category, Residence
from sqlalchemy.dialects.postgresql import json
from werkzeug.security import generate_password_hash, check_password_hash

main = Blueprint('main', __name__)


@main.route('/')
def index():
    posts = db.session.query(Magazine)
    category_id = request.args.get('category_id') or ''
    residence_id = request.args.get('residence_id') or ''
    if category_id:
        posts = posts.filter(Magazine.category_id == category_id)
    if residence_id:
        posts = posts.filter(Magazine.residence_id == residence_id)
    posts = posts.order_by(Magazine.id.desc()).all()
    categories = db.session.query(Category).all()
    residences = db.session.query(Residence).all()
    return render_template(current_app.config['TEMPLATE_THEME'] + '/magazines/list.html',
                           posts=posts,
                           categories=categories,
                           residences=residences,
                           category_id=category_id,
                           residence_id=residence_id)


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate():
            user = db.session.query(User).filter_by(email = form.email.data).one()
            if user:
                if not check_password_hash(user.password, form.password.data):
                    flash('password is wrong')
                else:
                    session['user_id'] = user.email
                    # flash('Successfully logged in as %s' % form.user.username)
                    return redirect(url_for('main.index'))
            else:
                flash('there is no your ID')

    return render_template(current_app.config['TEMPLATE_THEME'] + '/main/login.html', form=form)


@main.route('/join', methods=['GET', 'POST'])
def join():
    form = JoinForm(request.form)
    if request.method == 'POST':
        if form.validate():
            user = User()
            user.email = form.email.data
            user.name = form.name.data
            user.password = generate_password_hash(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('가입을 축하합니다.')
            return redirect(url_for('main.login'))

    return render_template(current_app.config['TEMPLATE_THEME'] + '/main/join.html', form=form)


@main.route('/login/facebook', methods=['POST'])
def signUpUser():
    accessToken = request.form['accessToken'];

    name = 'facebook user'
    if db.session.query(User).filter(User.accesscode == accessToken) is None:
        user = User()
        user.name = name
        user.accesscode = accessToken
        db.session.add(user)
        db.session.commit()
        return json.dumps({'status': 'OK', 'accessToken': accessToken})

    return json.dumps({'status': 'OK', 'accessToken': accessToken})


@main.route('/users')
def user_list():
    return render_template(current_app.config['TEMPLATE_THEME'] + '/main/user_list.html', users=User.query.all())
