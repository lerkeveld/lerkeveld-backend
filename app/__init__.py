from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
app.config.from_object('secret')

# flask_sqlalchemy for database connections
db = SQLAlchemy(app)

# flask_marschmallow for object serialization/deserialization
ma = Marshmallow(app)

# flask_jwt_extended for authentication
jwt = JWTManager(app)

# flask_mail for email
mail = Mail(app)

# flask_cors for CORS
cors = CORS(app)

# Avoid circular import: views need app variable
from app.admin import admin_blueprint
from app.api import api_blueprint
from app.token import token_blueprint

app.register_blueprint(admin_blueprint)
app.register_blueprint(api_blueprint)
app.register_blueprint(token_blueprint)

# Avoid circular import: models need app variable
import app.models as models


@jwt.user_lookup_loader
def load_user(jwt_header, jwt_payload):
    """
    The callback for reloading a user from the session.
    """
    try:
        return models.User.query.get(int(jwt_payload[app.config['JWT_IDENTITY_CLAIM']]))
    except ValueError:
        return None
