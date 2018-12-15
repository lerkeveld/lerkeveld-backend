import flask_jwt_extended as jwt
from flask import request, jsonify
from flask_restful import Resource

from app.api import api
from app.models import User
from .schema import LoginSchema

login_schema = LoginSchema()


@api.resource('/auth/login')
class LoginResource(Resource):

    def post(self):
        json_data = request.get_json()
        data, errors = login_schema.load(json_data)
        if not data or errors:
            return {'msg': '400 Bad Request', 'errors': errors}, 400

        email = data.get('email')
        password = data.get('password')

        user = User.get_by_email(email)

        if user and user.check_password(password):
            if not user.is_activated:
                return {'msg': 'Activeer je account'}, 403

            access_token = jwt.create_access_token(identity=user.id)
            refresh_token = jwt.create_refresh_token(identity=user.id)
            resp = jsonify({
                'success': True,
                'x-csrf-token': jwt.get_csrf_token(access_token)
            })
            jwt.set_access_cookies(resp, access_token)
            jwt.set_refresh_cookies(resp, refresh_token)
            return resp

        return {'msg': 'Fout e-mailadres of wachtwoord'}, 401


@api.resource('/auth/logout')
class LogoutResource(Resource):

    def post(self):
        resp = jsonify({'success': True})
        jwt.unset_jwt_cookies(resp)
        return resp


@api.resource('/auth/refresh')
class RefreshResource(Resource):

    @jwt.jwt_refresh_token_required
    def post(self):
        user = jwt.get_jwt_identity()
        access_token = jwt.create_access_token(identity=user)
        resp = jsonify({
            'success': True,
            'x-csrf-token': jwt.get_csrf_token(access_token)
            })
        jwt.set_access_cookies(resp, access_token)
        return resp
