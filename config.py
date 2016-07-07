class Config(object):
    DEBUG = False
    TESTING = False
    DEVELOPMENT = False
    CSRF_ENABLED = True
    SECRET_KEY = 'secret'
    TEMPLATE_THEME = 'bootstrap'
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'mysql://root:1miglobal@inotone.cjj0w56trea4.ap-northeast-2.rds.amazonaws.com/happyathome'


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
