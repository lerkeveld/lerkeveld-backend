from flask_restful import Resource

from app.api import api


@api.resource('/user/')
class UserResource(Resource):

    def get(self):
        return {}
