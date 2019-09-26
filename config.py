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
JWT_TOKEN_LOCATION = ['cookies']
JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours=1)
JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(days=90)
JWT_SECRET_KEY = SECRET_KEY
JWT_ACCESS_COOKIE_PATH = '/'
JWT_REFRESH_COOKIE_PATH = '/api/auth/refresh'
JWT_COOKIE_SECURE = True
JWT_COOKIE_DOMAIN = None
JWT_SESSION_COOKIE = False
JWT_COOKIE_SAMESITE = 'Strict'
JWT_COOKIE_CSRF_PROTECT = True
JWT_CSRF_IN_COOKIES = False

# flask_cors
CORS_ORIGINS = []
CORS_METHODS = ['GET', 'HEAD', 'POST', 'OPTIONS', 'PUT', 'PATCH', 'DELETE']
CORS_ALLOW_HEADERS = ['Content-Type', 'X-CSRF-TOKEN']
CORS_EXPOSE_HEADERS = None
CORS_SUPPORTS_CREDENTIALS = False
CORS_MAX_AGE = datetime.timedelta(days=1)
CORS_VARY_HEADER = True

# flask_mail
MAIL_SUPPRESS_SEND = True

# mailinglist
MAIL_KOTBAR_ADMIN = []
MAIL_MATERIAAL_ADMIN = []

# kotbar reservations
TOKEN_KOTBAR_RESERVATIONS = os.urandom(64)

# bem overview
TOKEN_BREAD_RESERVATIONS = os.urandom(64)

# itsdangerous
TOKEN_MAX_AGE = 2 * 24 * 60 * 60
