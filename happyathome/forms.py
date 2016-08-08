from flask_sqlalchemy import xrange
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from wtforms.validators import Email, Length, EqualTo, DataRequired
from math import ceil

validators = {
    'email': [
        DataRequired(),
        Email(message='Email 형식이 맞지 않습니다.')
    ],
    'password': [
        DataRequired(),
        Length(min=6, max=50),
        EqualTo('confirm', message='동일한 비밀번호를 입력해주세요.')
    ],

    'password_login': [
        DataRequired()
    ],
    'name': [
        DataRequired(),
        Length(min=2, max=35)
    ],
    'agreement': [
        DataRequired()
    ]
}


class ProfessionalUpdateForm(Form):
    name = StringField('이름')
    business_no = StringField('"-"를 포함하세요')
    address = StringField('ex) 경기도 수원시 장안구 창훈로 19번길 6 00빌딩 000호')
    phone = StringField('ex) 010-0000-0000')
    homepage = StringField('http://')


class PasswordUpdateForm(Form):
    password = PasswordField('변경을 원하는 비밀번호를 입력하세요', validators['password'])
    confirm = PasswordField('변경을 원하는 비밀번호 한번 더 입력하세요')


class UpdateForm(Form):
    name = StringField('이름')
    email = StringField('이메일', validators['email'])


class JoinForm(Form):
    name = StringField('이름')
    email = StringField('이메일', validators['email'])
    password = PasswordField('비밀번호', validators['password'])
    confirm = PasswordField('비밀번호 확인')
    agreement = BooleanField('동의', validators['agreement'])
    business_no = StringField('사업자번호('"-"'를 포함하세요)')


class LoginForm(Form):
    email = StringField('이메일', validators['email'])
    password = PasswordField('비밀번호', validators['password_login'])


class Pagination(object):
    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
        last = 0
        for num in xrange(1, self.pages + 1):
            if num <= left_edge or \
                    (self.page - left_current - 1 < num < self.page + right_current) or \
                    num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num
