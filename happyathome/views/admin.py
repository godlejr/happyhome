from flask import current_app, session, url_for, g
from flask_admin import BaseView, expose, AdminIndexView
from flask_admin.contrib import sqla
from flask_login import current_user
from happyathome import User
from happyathome.models import Category, Magazine, Photo, Comment, db, Board
from werkzeug.utils import redirect


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_admin

    @expose('/')
    def index(self):
        return super(MyAdminIndexView, self).index()


# admin class
class UserAdmin(sqla.ModelView):
    column_display_pk = True
    # Disable model creation

    # Override displayed fields
    column_list = ('id', 'name', 'email', 'authenticated', 'accesscode')  # column 이름변견
    form_columns = ['name', 'email', 'authenticated', 'accesscode']  # form 변경사항 저장
    column_searchable_list = ('name', 'email', 'authenticated', 'accesscode')  # 검색 기준설정

    # change field name
    column_labels = dict(id='No', name='이름', email='이메일', authenticated='인증', accesscode='소셜아이디')

    def is_accessible(self):
        return current_user.is_admin


class ClassAdminPhoto( sqla.ModelView):
    column_display_pk = True

    # Override displayed fields
    column_list = ('user', 'file', 'content')  # column 이름변견
    form_columns = ['user', 'file', 'content', 'magazine']
    column_searchable_list = (User.name, User.email, Photo.content)
    # change field name
    column_labels = dict(user='사용자', file='파일', content='내용', magazine='매거진')

    def is_accessible(self):
        return current_user.is_admin


class ClassAdminMagazine(sqla.ModelView):
    column_display_pk = True

    column_list = ('user', 'category', 'title', 'content')
    form_columns = ['user', 'category', 'title', 'content', 'photos']
    column_searchable_list = (User.name, User.email, Category.name, Magazine.title, Magazine.title)

    column_labels = dict(user='사용자', category='범주', title='제목', content='내용', photos='사진들')


class CommentAdminFile(sqla.ModelView):
    column_display_pk = True
    column_list = ('user', 'content')
    form_columns = ['user', 'content']
    column_searchable_list = (User.name, User.email, Comment.content)

    column_labels = dict(user='사용자', content='내용')


class BoardAdminFile(sqla.ModelView):
    column_display_pk = True

    column_list = ('user', 'content')
    form_columns = ['user', 'content']
    column_searchable_list = (User.name, User.email, Board.content)

    column_labels = dict(user='사용자', content='내용')


