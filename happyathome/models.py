from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import asc

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

    name = db.Column(db.Unicode(255), nullable=False)
    email = db.Column(db.Unicode(255), nullable=False, unique=True)
    password = db.Column(db.Unicode(255), nullable=False)
    authenticated = db.Column(db.Boolean, default=False)

    def is_authenticated(self):
        """Email 인증 여부 확인"""
        return self.authenticated


class Category(db.Model, BaseMixin):
    """카테고리 정보"""
    __tablename__ = 'categories'

    name = db.Column(db.Unicode(255), nullable=False)


class File(db.Model, BaseMixin):
    """파일 정보"""
    __tablename__ = 'files'

    type = db.Column(db.Integer, nullable=False)
    name = db.Column(db.Unicode(255), nullable=False)
    ext = db.Column(db.Unicode(255), nullable=False)
    size = db.Column(db.Integer, nullable=False)


class Photo(db.Model, BaseMixin):
    """사진 정보"""
    __tablename__ = 'photos'

    content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'))

    user = db.relationship('User', backref='user_photos')
    file = db.relationship('File', backref='file_photos')
    comments = db.relationship('Comments', backref='comment_photo')
    magazines = db.relationship('MagazinesPhotos', back_populates="photo")


class Comments(db.Model, BaseMixin):
    """사진 정보"""
    __tablename__ = 'comments'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    photo_id = db.Column(db.Integer, db.ForeignKey('photos.id'))
    type = db.Column(db.Unicode(1), nullable=False)
    content = db.Column(db.Text, nullable=False)

    user = db.relationship('User', backref='user_comments')


class Magazine(db.Model, BaseMixin):
    """매거진 정보"""
    __tablename__ = 'magazines'

    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'))
    title = db.Column(db.Unicode(255), nullable=False)
    content = db.Column(db.Text)

    user = db.relationship('User', backref='user_magazines')
    category = db.relationship('Category', backref='category_magazines')
    file = db.relationship('File', backref='file_magazines')
    photos = db.relationship('MagazinesPhotos', order_by=asc('magazines_photos.photo_id'), back_populates="magazine")


class MagazinesPhotos(db.Model, BaseMixin):
    """매거진-포토 연결고리"""
    __tablename__ = 'magazines_photos'

    magazine_id = db.Column(db.Integer, db.ForeignKey('magazines.id'))
    photo_id = db.Column(db.Integer, db.ForeignKey('photos.id'))

    magazine = db.relationship("Magazine", back_populates="photos")
    photo = db.relationship("Photo", back_populates="magazines")
