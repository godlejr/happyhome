import sys
from flask_sqlalchemy import SQLAlchemy
from markupsafe import Markup
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from sqlalchemy.orm import backref
from sqlalchemy.util import hybridmethod

db = SQLAlchemy()


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance


def del_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs)
    if instance.first():
        instance.delete()
    else:
        instance = model(**kwargs)
        session.add(instance)
    session.commit()


class BaseMixin(object):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    @property
    def created_date(self):
        return self.created_at.strftime('%Y-%m-%d')

    @property
    def updated_date(self):
        return self.updated_at.strftime('%Y-%m-%d')


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
    accesscode = db.Column(db.Unicode(255), nullable=False, unique=True)
    level = db.Column(db.Integer)
    cover = db.Column(db.Unicode(255))
    avatar = db.Column(db.Unicode(255))

    follow = db.relationship('Follow', back_populates='user')

    @hybridmethod
    def follow_check(self, session_id, follow_id):
        return db.session.query(Follow).filter(Follow.user_id == session_id).filter(
            Follow.follow_id == follow_id).first()

    @hybridmethod
    def following_count(self, user_id):
        return db.session.query(Follow).filter(Follow.user_id == user_id).count()

    @hybridmethod
    def follower_count(self, user_id):
        return db.session.query(Follow).filter(Follow.follow_id == user_id).count()

    @hybridmethod
    def follow_user(self, id):
        return db.session.query(User).filter(User.id == id).first()

    def is_authenticated(self):
        """Email 인증 여부 확인"""
        return self.authenticated

    def __repr__(self):
        return "%s(%s)" % (self.name, self.email)


class Category(db.Model, BaseMixin):
    """카테고리 정보"""
    __tablename__ = 'categories'

    name = db.Column(db.Unicode(50), nullable=False)

    def __repr__(self):
        return self.name


class Follow(db.Model, BaseMixin):
    """팔로우 정보"""
    __tablename__ = 'follows'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    follow_id = db.Column(db.Integer, nullable=False)

    user = db.relationship('User', back_populates='follow')


class Residence(db.Model, BaseMixin):
    """거주지 정보"""
    __tablename__ = 'residences'

    name = db.Column(db.Unicode(50), nullable=False)


class Room(db.Model, BaseMixin):
    """공간 정보"""
    __tablename__ = 'rooms'

    name = db.Column(db.Unicode(50), nullable=False)


class File(db.Model, BaseMixin):
    """파일 정보"""
    __tablename__ = 'files'

    type = db.Column(db.Integer, nullable=False, default=1)
    name = db.Column(db.Unicode(255), nullable=False)
    ext = db.Column(db.Unicode(255), nullable=False)
    size = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return Markup('<img src="http://static.inotone.co.kr/data/img/%s" / width="100" height="100">') % self.name


class Comment(db.Model, BaseMixin):
    """댓글 내역"""
    __tablename__ = 'comments'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    content = db.Column(db.Text, nullable=False)
    comment_id = db.Column(db.Integer)

    user = db.relationship('User', backref=backref('user_comments'))
    photos = db.relationship('PhotoComment', back_populates='comment')
    magazines = db.relationship('MagazineComment', back_populates='comment')


class Photo(db.Model, BaseMixin):
    """사진 정보"""
    __tablename__ = 'photos'

    content = db.Column(db.Text)
    hits = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'))
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'))
    magazine_id = db.Column(db.Integer, db.ForeignKey('magazines.id'))

    user = db.relationship('User', backref=backref('user_photos'))
    file = db.relationship('File', backref=backref('file_photos'))
    room = db.relationship('Room', backref=backref('room_photos'))
    magazine = db.relationship('Magazine', back_populates='photos')
    comments = db.relationship('PhotoComment', back_populates='photo')

    @hybrid_method
    def is_active(self, model, user_id):
        return getattr(sys.modules[__name__], model).query.filter_by(photo_id=self.id, user_id=user_id).first()


class PhotoLike(db.Model, BaseMixin):
    """포토-좋아요 연결고리"""
    __tablename__ = 'photo_likes'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    photo_id = db.Column(db.Integer, db.ForeignKey('photos.id'))

    user = db.relationship('User', backref='like_users')
    photo = db.relationship('Photo', backref='like_photos')


class PhotoScrap(db.Model, BaseMixin):
    """포토-좋아요 연결고리"""
    __tablename__ = 'photo_scraps'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    photo_id = db.Column(db.Integer, db.ForeignKey('photos.id'))

    user = db.relationship('User', backref='scrap_users')
    photo = db.relationship('Photo', backref='scrap_photos')


class PhotoComment(db.Model, BaseMixin):
    """포토-댓글 연결고리"""
    __tablename__ = 'photo_comments'

    photo_id = db.Column(db.Integer, db.ForeignKey('photos.id'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'))

    photo = db.relationship('Photo', back_populates='comments')
    comment = db.relationship('Comment', back_populates='photos')


class Magazine(db.Model, BaseMixin):
    """매거진 정보"""
    __tablename__ = 'magazines'

    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    residence_id = db.Column(db.Integer, db.ForeignKey('residences.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.Unicode(255), nullable=False)
    size = db.Column(db.Unicode(255))
    location = db.Column(db.Unicode(255))
    cost = db.Column(db.Unicode(255))
    content = db.Column(db.Text)
    hits = db.Column(db.Integer)

    user = db.relationship('User', backref=backref('user_magazines'))
    category = db.relationship('Category', backref=backref('category_magazines'))
    residence = db.relationship('Residence', backref=backref('residence_magazines'))
    photos = db.relationship('Photo', back_populates='magazine')
    comments = db.relationship('MagazineComment', back_populates='magazine')

    @hybrid_property
    def vr_count(self):
        return db.session.query(Photo).filter(Photo.magazine_id == self.id).filter(Photo.file.has(type=2)).count()

    @hybrid_property
    def mov_count(self):
        return db.session.query(Photo).filter(Photo.magazine_id == self.id).filter(Photo.file.has(type=3)).count()

    @hybrid_method
    def is_active(self, model, user_id):
        return getattr(sys.modules[__name__], model).query.filter_by(photo_id=self.id, user_id=user_id).first()


class MagazineComment(db.Model, BaseMixin):
    """매거진-댓글 연결고리"""
    __tablename__ = 'magazine_comments'

    magazine_id = db.Column(db.Integer, db.ForeignKey('magazines.id'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'))

    magazine = db.relationship('Magazine', back_populates='comments')
    comment = db.relationship('Comment', back_populates='magazines')


class Social(db.Model, BaseMixin):
    __tablename__ = 'socials'

    social_id = db.Column(db.String(64), nullable=False, primary_key=True)
    nickname = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=True)


class Professional(db.Model, BaseMixin):
    """전문가 정보"""
    __tablename__ = 'professionals'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    business_no = db.Column(db.Unicode(15), nullable=False)
    phone = db.Column(db.Unicode(15))
    address = db.Column(db.Unicode(255))
    homepage = db.Column(db.Unicode(45))
    greeting = db.Column(db.Text)

    user = db.relationship('User', backref=backref('user_professionals'))
