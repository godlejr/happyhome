from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, session, message_flashed
from happyathome.forms import JoinForm, LoginForm
from happyathome.models import db, User, Magazine, Professional, Photo
from sqlalchemy.dialects.postgresql import json
from werkzeug.security import generate_password_hash, check_password_hash

main = Blueprint('main', __name__)


@main.context_processor
def utility_processor():
    def url_for_s3(s3path, filename=''):
        return ''.join((current_app.config['S3_BUCKET_NAME'], current_app.config[s3path], filename))
    return dict(url_for_s3=url_for_s3)


@main.route('/')
def index():
    magazines = Magazine.query.order_by(Magazine.id.desc()).limit(6).all()
    photos = Photo.query.order_by(Photo.id.desc()).limit(6).all()
    return render_template(current_app.config['TEMPLATE_THEME'] + '/main/index.html', magazines=magazines, photos=photos)


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate():
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                if not check_password_hash(user.password, form.password.data):
                    flash('비밀번호가 잘못되었습니다.')
                else:
                    session['user_id'] = user.id
                    session['user_email'] = user.email
                    session['user_level'] = user.level
                    return redirect(request.args.get('next', url_for('main.index')))
            else:
                flash('회원아이디가 잘못되었습니다.')
    return render_template(current_app.config['TEMPLATE_THEME'] + '/main/login.html', form=form)


@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))


@main.route('/join', methods=['GET', 'POST'])
def join():
    form = JoinForm(request.form)
    if request.method == 'POST':
        if form.validate():
            user = User()
            if User.query.filter_by(email = form.email.data).first():
                flash('사용중인 이메일입니다.')
                return render_template(current_app.config['TEMPLATE_THEME'] + '/main/join.html', form=form)

            user.email = form.email.data
            user.name = form.name.data
            user.password = generate_password_hash(form.password.data)

            if request.form['login_check'] == '2':
                user.level = 2
                db.session.add(user)
                db.session.commit()

                professional = Professional()
                professional.business_no = form.business_no.data
                professional.user_id = user.id
                db.session.add(professional)
                db.session.commit()
            else:
                user.level = 1
                db.session.add(user)
                db.session.commit()

            flash('가입을 축하합니다.')
            return redirect(url_for('main.login'))

    return render_template(current_app.config['TEMPLATE_THEME'] + '/main/join.html', form=form)


@main.route('/privacy', methods=['GET', 'POST'])
def privacy():
    return render_template(current_app.config['TEMPLATE_THEME'] + '/main/privacy.html')


@main.route('/agreement', methods=['GET', 'POST'])
def agreement():
    return render_template(current_app.config['TEMPLATE_THEME'] + '/main/agreement.html')



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
