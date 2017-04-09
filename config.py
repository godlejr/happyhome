import os


class Config(object):
    DEBUG = False
    TESTING = False
    DEVELOPMENT = False
    CSRF_ENABLED = True
    SECRET_KEY = 'secret'
    TEMPLATE_THEME = 'bootstrap'
    NO_IMG = 'noimg.JPG'
    REDIS_URL = 'redis://52.78.113.21/0'
    S3_BUCKET_NAME = 'http://static.inotone.co.kr'
    S3_IMG_DIRECTORY = '/data/img/'
    S3_USER_DIRECTORY = '/data/user/'
    S3_COVER_DIRECTORY = '/data/cover/'
    UPLOAD_TMP_DIRECTORY = '/tmp/'
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USERNAME = 'dev@inotone.co.kr'
    MAIL_PASSWORD = 'xxxxxxxx'
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False

    YOUTUBE_API_SCOPES = ['https://www.googleapis.com/auth/youtube']
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"

    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_POOL_TIMEOUT = 10
    SQLALCHEMY_POOL_RECYCLE = 1800
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'mysql://root:1miglobal@inotone.cjj0w56trea4.ap-northeast-2.rds.amazonaws.com/happyathome'
    SOCIAL_FACEBOOK = {
        'consumer_key': 'xxxxxxxx',
        'consumer_secret': 'xxxxxxxxx'
    }


class ProductionConfig(Config):
    DEBUG = False
    REDIS_URL = '52.78.113.21'
    TEMPLATE_THEME = 'bootstrap'
    SECRET_KEY = os.getenv('SECRET_KEY') or 'xxxxxxxxxx'


class StagingConfig(Config):
    DEBUG = True


class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False


class TestingConfig(Config):
    TESTING = True


def init_app(app, config_name):
    app.config.from_object({
        'testing': TestingConfig,
        'production': ProductionConfig,
        'development': DevelopmentConfig,
        'default': DevelopmentConfig
    }[config_name]())
