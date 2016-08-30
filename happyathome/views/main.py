import os

import shortuuid
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, session, jsonify
from flask_mail import Mail, Message
from happyathome.forms import JoinForm, LoginForm
from happyathome.models import db, User, Magazine, Professional, Photo
from oauth2client import client
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
                    return redirect(request.args.get("next") or url_for('main.index'))
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
        if User.query.filter_by(email=request.form.get('email')).first():
            flash('사용중인 이메일입니다.')
        if form.validate():
            user = User()
            if User.query.filter_by(email=request.form.get('email')).first():
                return redirect(url_for('main.join'))

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
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            password_token = shortuuid.uuid()
            current_app.redis.append(password_token, form.email.data)
            current_app.redis.expire(password_token, 3600)

            msg = Message('해피홈 비밀번호 변경 메일', sender='해피홈', recipients=[form.email.data])
            msg.html = '''
                <div style="width:600px;border:1px solid #e0e0e0">
                    <div style="padding:8px 20px">
                        <div style="float:left;margin-top:8px;"><span style="cursor:pointer;display:inline-block;line-height:33px;width:112px;height:33px;background-size:112px 33px;background-repeat:no-repeat;background-position:center;background-image:url(http://static.inotone.co.kr/img/happyathome.png)"></span></div>
                        <div style="text-align:right;margin-left:100px;padding-top:30px;font-size:14px;font-family:'맑은 고딕',sans-serif">행복공간 크리에이터</div>
                    </div>
                    <div style="font-size:14px;padding:60px 40px;background-color:#f4f4f4;border-top:3px solid #303030;box-sizing:border-box">
                        <div style="font-family:'맑은 고딕',sans-serif">
                            <p style="font-size:14px;margin:10px 0">{0}님, 안녕하세요.</p>
                            <p style="font-size:14px;margin:10px 0">비밀번호 재설정 안내 메일입니다.</p>
                            <p style="font-size:14px;margin:10px 0">* 만약 본인이 비밀번호 재설정 신청을 한 것이 아니라면, 본 메일을 무시해주세요.</p>
                            <p style="font-size:14px;margin:10px 0">{0}님이 비밀번호를 변경하기 전에는 계정의 비밀번호는 바뀌지 않습니다.</p>
                        </div>
                        <div style="margin-top:60px;text-align:center">
                            <a href="http://www.happyathome.co.kr/confirm_key?key={1}" target="_blank" style="cursor:pointer;color:#ffffff;font-size:14px;font-weight:700;padding:7px 30px;border:1px solid #46AB76;background-color:#5EB788;text-decoration:none;font-family:'맑은 고딕',sans-serif">비밀번호 재설정 하러가기</a>
                        </div>
                    </div>
                    <div style="padding:10px 40px;color:#b4b4b4;background-color:#54595D;box-sizing:border-box;font-family:'맑은 고딕',sans-serif">
                        <p style="font-size:12px;margin:2px 0">상호명 | INOTONE</p>
                        <p style="font-size:12px;margin:2px 0">대표이사 | 김경태</p>
                        <p style="font-size:12px;margin:2px 0">사업자등록번호 | 478-86-00420</p>
                        <p style="font-size:12px;margin:2px 0">주소 | 서울특별시 강남구 봉은사로84길 8, 5층(삼성동, 유승빌딩)</p>
                        <p style="font-size:12px;margin:2px 0">이메일 | contact@inotone.co.kr</p>
                        <p style="font-size:12px;margin:2px 0">Copyright (C)2016 by Inotone Co., LTD. All Rights Reserved</p>
                    </div>
                </div>
            '''.format(user.name, password_token)
            mail.send(msg)
            flash('기존 이메일로 비밀번호변경 관련 url을 보냈습니다. 확인해주세요.')
        return redirect(url_for('main.login'))
    return render_template(current_app.config['TEMPLATE_THEME'] + '/main/password.html', form=form)


@main.route('/facebook_login', methods=['POST'])
def facebook_login():
    userName = request.form.get('user_name')
    userEmail = request.form.get('user_email')
    user = db.session.query(User).filter(User.email == userEmail).first()

    if not user:
        user = User()
        user.email = userEmail
        user.name = userName
        user.password ="ABLFJBDALSJFBU10!@*#!2820"
        user.level = 1
        db.session.add(user)
        db.session.flush()
        db.session.commit()

    session['user_id'] = user.id
    session['user_email'] = user.email
    session['user_level'] = user.level

    return jsonify({
        'ok': 1
    })
