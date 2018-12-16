from flask import Blueprint

token_blueprint = Blueprint('token', __name__, url_prefix='/token')


# Avoid circular import: views need token_blueprint variable
import app.token.views