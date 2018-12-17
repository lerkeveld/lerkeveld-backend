import flask_jwt_extended as jwt
from flask_restful import Resource

from app.api import api
from .schema import UserSchema

user_schema = UserSchema()


@api.resource('/user/profile')
class UserResource(Resource):

    @jwt.jwt_required
    def get(self):
        user = jwt.current_user
        data, _ = user_schema.dump(user)
        return {'success': True, 'user': data}
