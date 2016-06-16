from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class BaseMixin(object):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return self.__dict__


class User(db.Model, BaseMixin):
    """사용자 계정 정보

    :param str email: Email 주소 사용자 ID로 사용
    :param str password: 엄호화된 패스워드
    """
    __tablename__ = 'users'

    email = db.Column(db.Unicode(255), nullable=False, unique=True)
    password = db.Column(db.Unicode(255), nullable=False)
    authenticated = db.Column(db.Boolean, default=False)

    def is_authenticated(self):
        """Email 인증 여부 확인"""
        return self.authenticated


class Post(db.Model, BaseMixin):
    """포스트 정보"""
    __tablename__ = 'posts'

    user_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.Unicode(255), nullable=False)
    content = db.Column(db.Unicode(255))


class Photo(db.Model, BaseMixin):
    """사진 정보"""
    __tablename__ = 'photos'
    
    post_id = db.Column(db.Integer, nullable=False)
    filename = db.Column(db.Unicode(255), nullable=False)
    filesize = db.Column(db.Integer, nullable=False)
