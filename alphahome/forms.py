from wtforms import Form, BooleanField, StringField, PasswordField, validators


class JoinForm(Form):
    email = StringField('이메일', [validators.Length(min=6, max=35)])
    password = PasswordField('비밀번호', [
        validators.DataRequired()
    ])
    agreement = BooleanField('이용약관', [validators.DataRequired()])
