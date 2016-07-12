from wtforms import Form, BooleanField, StringField, PasswordField, validators
from wtforms.validators import Required, Email, Length, Regexp, EqualTo, DataRequired


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


