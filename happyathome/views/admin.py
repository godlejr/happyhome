from flask import current_app
from flask_admin import BaseView, expose
from flask_admin.contrib import sqla
from happyathome import User
from happyathome.models import Category, Magazine, Photo, Comment


class MyView(BaseView):
    @expose('/')
    def User(self):
        return self.render(current_app.config['TEMPLATE_THEME'] + '/admin/index.html')


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


class ClassAdminPhoto(sqla.ModelView):
    column_display_pk = True

    # Override displayed fields
    column_list = ('user', 'file', 'content')  # column 이름변견
    form_columns = ['user', 'file', 'content', 'magazine']
    column_searchable_list = (User.name, User.email, Photo.content)
    # change field name
    column_labels = dict(user='사용자', file='파일', content='내용', magazine='매거진')


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
