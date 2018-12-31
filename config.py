import os
import datetime

# flask
SECRET_KEY = os.urandom(64)

# https://github.com/vimalloc/flask-jwt-extended/issues/86
PROPAGATE_EXCEPTIONS = True

# flask_sqlalchemy
SQLALCHEMY_DATABASE_URI = ''
SQLALCHEMY_TRACK_MODIFICATIONS = False

# flask_jwt_extended
JWT_SECRET_KEY = os.urandom(64)
JWT_TOKEN_LOCATION = ['cookies']
JWT_COOKIE_CSRF_PROTECT = True
JWT_CSRF_IN_COOKIES = False
JWT_ACCESS_COOKIE_PATH = '/'
JWT_REFRESH_COOKIE_PATH = '/api/auth/refresh'
JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours=1)
JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(days=90)

# flask_cors
CORS_ORIGINS = []

# flask_mail
MAIL_SUPPRESS_SEND = True

# mailinglist
MAIL_KOTBAR_ADMIN = []
MAIL_MATERIAAL_ADMIN = []

# itsdangerous
TOKEN_MAX_AGE = 2 * 24 * 60 * 60
