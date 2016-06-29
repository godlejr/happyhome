from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
magazine_photos = db.Table('magazine_photos', db.metadata,
                           db.Column('magazine_id', db.Integer, db.ForeignKey('magazines.id')),
                           db.Column('photo_id', db.Integer, db.ForeignKey('photos.id'))
                           )


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
    interiors = db.relationship('Interior', backref='interior_users')
    snapshots = db.relationship('Snapshot', backref='snapshot_users')
    magazines = db.relationship('Magazine', backref='magazine_users')

    def is_authenticated(self):
        """Email 인증 여부 확인"""
        return self.authenticated


class Photo(db.Model, BaseMixin):
    """사진 정보"""
    __tablename__ = 'photos'

    filename = db.Column(db.Unicode(255), nullable=False)
    filesize = db.Column(db.Integer, nullable=False)


class Interior(db.Model, BaseMixin):
    """포스트 정보"""
    __tablename__ = 'interiors'

    title = db.Column(db.Unicode(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    photo_id = db.Column(db.Integer, db.ForeignKey('photos.id'))
    photos = db.relationship('Photo', backref='interior_photos')


class Snapshot(db.Model, BaseMixin):
    """포스트 정보"""
    __tablename__ = 'snapshots'

    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    photo_id = db.Column(db.Integer, db.ForeignKey('photos.id'))
    photos = db.relationship('Photo', backref='snapshot_photos')


class Magazine(db.Model, BaseMixin):
    """매거진 정보"""
    __tablename__ = 'magazines'

    title = db.Column(db.Unicode(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    content_txt = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    photos = db.relationship('Photo', secondary=magazine_photos, backref='magazines')
