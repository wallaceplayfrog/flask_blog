import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'hard to guess string'  # os.environ.get('SECRET_KEY') or 'hard to guess string'
    MAIL_SERVER = 'smtp.qq.com' # os.environ.get('MAIL_SERVER', 'smtp.qq.com')
    MAIL_PORT = 465  # int(os.environ.get('MAIL_PORT', '465'))
    MAIL_USE_TLS = False  # os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USE_SSL = True  # os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = '2425779559@qq.com'  # os.environ.get('MAIL_USERNAME') 
    MAIL_PASSWORD = 'clwstmhqcivudijc'  # os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = '2425779559@qq.com'  # os.environ.get('MAIL_DEFAULT_SENDER')
    MAIL_SUPPRESS_SEND = True
    
    FLASKY_FOLLOWERS_PER_PAGE = 50
    FLASKY_POSTS_PER_PAGE = 10
    FLASKY_MAIL_SUBJECT_PREFIX = '[FROGY]'
    FLASKY_MAIL_SENDER = 'Frogy@admin.com'
    FLASKY_ADMIN = '2425779559@qq.com'  # os.environ.get('FLASKY_ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite://'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data.sqlite')

config = {
    'development' : DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}