import marshmallow as ma

import flask_jwt_extended as jwt
from flask import request
from flask_restful import Resource

from app import db
from app.api import api
from app.models import User
from .schema import UserSchema, EditSchema, EditSecureSchema, PublicUserSchema

user_schema = UserSchema()
edit_schema = EditSchema()
edit_secure_schema = EditSecureSchema()
public_users_schema = PublicUserSchema(many=True)


@api.resource('/user/profile')
class UserResource(Resource):

    @jwt.jwt_required
    def get(self):
        user = jwt.current_user
        data = user_schema.dump(user)
        return {'success': True, 'user': data}


@api.resource('/user/edit')
class UserEditResource(Resource):

    @jwt.jwt_required
    def post(self):
        json_data = request.get_json()
        try:
            data = edit_schema.load(json_data)
        except ma.ValidationError as err:
            return {'msg': '400 Bad Request', 'errors': err.messages}, 400

        is_sharing = data.get('is_sharing')

        user = jwt.current_user
        if is_sharing is not None: user.is_sharing = is_sharing

        db.session.add(user)
        db.session.commit()
        return {'success': True}


@api.resource('/user/edit/secure')
class UserEditSecureResource(Resource):

    @jwt.jwt_required
    def post(self):
        json_data = request.get_json()
        try:
            data = edit_secure_schema.load(json_data)
        except ma.ValidationError as err:
            return {'msg': '400 Bad Request', 'errors': err.messages}, 400

        check = data.get('check')
        email = data.get('email')
        password = data.get('password')

        user = jwt.current_user
        if not user.check_password(check):
            return {'msg': 'Huidig wachtwoord incorrect'}, 400

        if email is not None: user.set_email(email)
        if password is not None: user.set_password(password)

        db.session.add(user)
        db.session.commit()
        return {'success': True}


@api.resource('/user/all')
class UsersResource(Resource):

    @jwt.jwt_required
    def get(self):
        users = User.query.all()
        data = public_users_schema.dump(users)
        return {'success': True, 'users': data}
