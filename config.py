import os
basedir = os.path.abspath(os.path.dirname(__file__))

# flask
SECRET_KEY = '<default>'

# flask_sqlalchemy
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# flask_jwt_extended
JWT_SECRET_KEY = '<default>'
JWT_ACCESS_COOKIE_PATH = '/'
JWT_REFRESH_COOKIE_PATH = '/api/auth/refresh'
JWT_TOKEN_LOCATION = ['cookies']
JWT_COOKIE_CSRF_PROTECT = True
JWT_CSRF_IN_COOKIES = False

# flask_cors
CORS_ORIGINS = []  # add the origin

# flask_mail
MAIL_DEFAULT_SENDER = ('Lerkeveld IT', '<default>')

# mailinglist
MAIL_KOTBAR_ADMIN = []

# itsdangerous
TOKEN_MAX_AGE = 2 * 24 * 60 * 60
