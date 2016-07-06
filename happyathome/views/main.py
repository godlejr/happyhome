from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from happyathome.forms import JoinForm
from happyathome.models import db, User, Snapshot

main = Blueprint('main', __name__)


@main.route('/')
def index():
    posts = db.session.query(Snapshot).all()
    return render_template(current_app.config['TEMPLATE_THEME'] + '/main/index.html', posts=posts)


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

    return render_template(current_app.config['TEMPLATE_THEME'] + '/main/join.html', form=form)


@main.route('/users')
def user_list():
    return render_template(current_app.config['TEMPLATE_THEME'] + '/main/user_list.html', users=User.query.all())

