class Config(object):
    DEBUG = False
    TESTING = False
    DEVELOPMENT = False
    CSRF_ENABLED = True
    SECRET_KEY = 'secret'
    TEMPLATE_THEME = 'bootstrap'
    REDIS_URL = 'dev.inotone.co.kr'
    REDIS_DATABASE = 0
    S3_BUCKET_NAME = 'http://static.inotone.co.kr'
    S3_IMG_DIRECTORY = '/data/img/'
    S3_USER_DIRECTORY = '/data/user/'
    S3_COVER_DIRECTORY = '/data/cover/'
    NO_IMG='noimg.JPG'
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    REDIS_URL = "dev.inotone.co.kr"
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_POOL_TIMEOUT = 10
    SQLALCHEMY_POOL_RECYCLE = 1800
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'mysql://root:1miglobal@inotone.cjj0w56trea4.ap-northeast-2.rds.amazonaws.com/happyathome'
    SOCIAL_FACEBOOK = {
        'consumer_key': '1743693419236952',
        'consumer_secret': '8462ffb5095aad6600f6acc6ad4146ea'
    }


class ProductionConfig(Config):
    DEBUG = False


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
