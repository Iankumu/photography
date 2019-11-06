import os

basedir = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = 'C:/Users/User/Documents/Strathmore/ICS/Academic Work/Year 2/Semester 2/IS Project/photography/static'
CLIENT_FOLDER = 'C:/Users/User/Documents/Strathmore/ICS/Academic Work/Year 2/Semester 2/IS Project/photography/static/Client_Uploads'


class Config(object):
    # alchemy configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # secret key
    # TODO:PUT secret key in environmental variables
    SECRET_KEY = 'secret123'
    SECURITY_PASSWORD_SALT = 'super-secret-random-salt'

    # config MYSQL
    MYSQL_HOST = '127.0.0.1'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''
    MYSQL_DB = 'photography'
    MYSQL_CURSORCLASS = 'DictCursor'

    # Email SMTP CONFIGURATION
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'danielavexus@gmail.com'  # yor email
    MAIL_PASSWORD = 'DanKingKaKa!'  # your email
    MAIL_DEFAULT_SENDER = 'danielavexus@gmail.com'  # your password
    # config image format
    UPLOAD_FOLDER = UPLOAD_FOLDER
    CLIENT_FOLDER = CLIENT_FOLDER
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024

    # FLASK SECURITY CONFIGURATIONS
    SECURITY_RECOVERABLE = True
    SECURITY_REGISTERABLE = True
    SECURITY_POST_LOGIN_VIEW = '/'
    SECURITY_TRACKABLE = True
    SECURITY_EMAIL_SENDER = os.environ.get('EMAIL_USER')
