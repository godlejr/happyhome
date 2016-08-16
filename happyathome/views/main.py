import shortuuid
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, session, message_flashed
from flask_mail import Mail, Message
from happyathome.forms import JoinForm, LoginForm
from happyathome.models import db, User, Magazine, Professional, Photo
from sqlalchemy.dialects.postgresql import json
from werkzeug.security import generate_password_hash, check_password_hash

main = Blueprint('main', __name__)
mail = Mail()


@main.context_processor
def utility_processor():
    def url_for_s3(s3path, filename=''):
        return ''.join((current_app.config['S3_BUCKET_NAME'], current_app.config[s3path], filename))
    return dict(url_for_s3=url_for_s3)


@main.route('/')
def index():
    magazines = Magazine.query.order_by(Magazine.hits.desc(), Magazine.id.desc()).limit(6).all()
    photos = Photo.query.order_by(Photo.hits.desc(), Photo.id.desc()).limit(6).all()
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

            if form.joiner.data == '2':
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


@main.route('/confirm_key', methods=['GET', 'POST'])
def confirm_key():
    if current_app.redis.get(request.args.get('key')):
        return redirect(url_for('main.edit_password', key=request.args.get('key')))
    return redirect(url_for('main.index'))


@main.route('/edit_password/<key>', methods=['GET', 'POST'])
def edit_password(key):
    form = JoinForm(request.form)
    if request.method == 'POST':
        if form.password.data.__eq__(form.confirm.data):
            email = current_app.redis.get(key)
            current_app.redis.delete(key)
            user = User.query.filter_by(email=email).first()
            user.password = generate_password_hash(form.password.data)
            db.session.add(user)
            db.session.commit()

            return redirect(url_for('main.index'))
        else:
            flash('동일한 비밀번호를 입력하세요')
    return render_template(current_app.config['TEMPLATE_THEME'] + '/main/edit_password.html',form=form)


@main.route('/password', methods=['GET', 'POST'])
def password():
    form = LoginForm(request.form)
    if request.method == 'POST':
        if User.query.filter_by(email=form.email.data).first():
            password_token = shortuuid.uuid()
            current_app.redis.append(password_token, form.email.data)
            current_app.redis.expire(password_token, 3600)

            msg = Message('Hello', sender='inotone.kr@google.com', recipients=[form.email.data])
            msg.html = '''
            <form action="http://www.happyathome.co.kr/confirm_key">
            <input hidden="hidden" name="key" value="%s"/>
            <button type="submit">비밀번호 변경url</button>
            </form>
           ''' %password_token
            mail.send(msg)
            flash('기존 이메일로 비밀번호변경 관련 url을 보냈습니다. 확인해주세요.')
        return redirect(url_for('main.login'))
    return render_template(current_app.config['TEMPLATE_THEME'] + '/main/password.html',form=form)


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
