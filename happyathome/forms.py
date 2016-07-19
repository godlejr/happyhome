from flask_sqlalchemy import xrange
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from wtforms.validators import Required, Email, Length, Regexp, EqualTo, DataRequired
from math import ceil

validators = {
    'email': [
        Required(),
        Email(message='not an email fomat!')
    ],
    'password': [
        Required(),
        Length(min=6, max=50),
        EqualTo('confirm', message='Passwords must match'),
       Regexp('[A-Za-z0-9@#$%^&+=]', message='Password contains invalid characters')
    ],
    'password_login':[
        Required()
    ],
    'name':[
        Required(),
        Length(min=2, max=35)
    ],
    'agreement':[
        DataRequired()
    ]
}


class JoinForm(Form):
    name = StringField('name',validators['name'])
    email = StringField('email',validators['email'])
    password = PasswordField('password',validators['password'])
    confirm = PasswordField('password confirm')
    agreement = BooleanField('agreement', validators['agreement'])


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

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in xrange(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and \
                num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num