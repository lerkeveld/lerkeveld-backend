from flask import Blueprint
from flask_restful import Api

api_blueprint = Blueprint('api', __name__, url_prefix='/api')
api = Api(api_blueprint)

# Avoid circular import: views need api variable
import app.api.auth.views
import app.api.user.views
