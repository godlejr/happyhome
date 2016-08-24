from flask import current_app, session, url_for, g
from flask_admin import BaseView, expose, AdminIndexView
from flask_admin.contrib import sqla
from flask_login import current_user
from happyathome import User
from happyathome.models import Category, Magazine, Photo, Comment, Board, Residence, Business


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        if not session.get('user_id'):
            return False
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


class ClassAdminCategory(sqla.ModelView):
    column_display_pk = True

    # Override displayed fields
    column_list = ('name',)
    form_columns = ('name',)
    column_searchable_list = (Category.id, Category.name)
    column_labels = dict(name='테마 이름')

    def is_accessible(self):
        return current_user.is_admin


class ClassAdminResidence(sqla.ModelView):
    column_display_pk = True

    # Override displayed fields
    column_list = ('name',)
    form_columns = ('name',)
    column_searchable_list = (Residence.id, Residence.name)
    column_labels = dict(name='장소 이름')

    def is_accessible(self):
        return current_user.is_admin


class ClassAdminBusiness(sqla.ModelView):
    column_display_pk = True

    # Override displayed fields
    column_list = ('name',)
    form_columns = ('name',)
    column_searchable_list = (Business.id, Business.name)
    column_labels = dict(name='업종 이름')

    def is_accessible(self):
        return current_user.is_admin


class ClassAdminPhoto(sqla.ModelView):
    column_display_pk = True

    # Override displayed fields
    column_list = ('user', 'file', 'content', 'hits')
    form_columns = ('user', 'file', 'content', 'hits', 'magazine')
    column_searchable_list = (User.name, User.email, Photo.content)
    column_labels = dict(user='사용자', file='파일', content='내용', hits='조회수', magazine='매거진')

    def is_accessible(self):
        return current_user.is_admin


class ClassAdminMagazine(sqla.ModelView):
    column_display_pk = True

    column_list = ('user', 'category', 'title', 'content', 'hits')
    form_columns = ['user', 'category', 'title', 'content', 'hits', 'photos']
    column_searchable_list = (User.name, User.email, Category.name, Magazine.title, Magazine.content)

    column_labels = dict(user='사용자', category='범주', title='제목', content='내용', hits='조회수', photos='사진들')

    def is_accessible(self):
        return current_user.is_admin


class CommentAdminFile(sqla.ModelView):
    column_display_pk = True
    column_list = ('user', 'content')
    form_columns = ['user', 'content']
    column_searchable_list = (User.name, User.email, Comment.content)

    column_labels = dict(user='사용자', content='내용')

    def is_accessible(self):
        return current_user.is_admin


class BoardAdminFile(sqla.ModelView):
    column_display_pk = True

    column_list = ('user', 'content')
    form_columns = ['user', 'content']
    column_searchable_list = (User.name, User.email, Board.content)

    column_labels = dict(user='사용자', content='내용')

    def is_accessible(self):
        return current_user.is_admin

