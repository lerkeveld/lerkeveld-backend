import flask_jwt_extended as jwt
from flask import request, jsonify
from flask_restful import Resource

from app import db
from app import emails
from app.api import api
from app.models import User
from .schema import LoginSchema, ActivateSchema, ResetSchema

login_schema = LoginSchema()
activate_schema = ActivateSchema()
reset_schema = ResetSchema()


@api.resource('/auth/login')
class LoginResource(Resource):

    def post(self):
        json_data = request.get_json()
        try:
            data = login_schema.load(json_data)
        except ma.ValidationError as err:
            return {'msg': '400 Bad Request', 'errors': err.messages}, 400

        email = data.get('email')
        password = data.get('password')

        user = User.get_by_email(email)

        if user and user.check_password(password):
            if not user.is_activated:
                return {'msg': 'Activeer je account'}, 403

            access_token = jwt.create_access_token(identity=user.id)
            refresh_token = jwt.create_refresh_token(identity=user.id)
            response = jsonify({
                'success': True,
                'a-csrf-token': jwt.get_csrf_token(access_token),
                'r-csrf-token': jwt.get_csrf_token(refresh_token)
            })
            jwt.set_access_cookies(response, access_token)
            jwt.set_refresh_cookies(response, refresh_token)
            return response

        return {'msg': 'Fout e-mailadres of wachtwoord'}, 401


@api.resource('/auth/logout')
class LogoutResource(Resource):

    def post(self):
        response = jsonify({'success': True})
        jwt.unset_jwt_cookies(response)
        return response


@api.resource('/auth/refresh')
class RefreshResource(Resource):

    @jwt.jwt_refresh_token_required
    def post(self):
        user = jwt.get_jwt_identity()
        access_token = jwt.create_access_token(identity=user)
        response = jsonify({
            'success': True,
            'a-csrf-token': jwt.get_csrf_token(access_token),
            })
        jwt.set_access_cookies(response, access_token)
        return response


@api.resource('/auth/activate')
class ActivateResource(Resource):

    def post(self):
        json_data = request.get_json()
        try:
            data = activate_schema.load(json_data)
        except ma.ValidationError as err:
            return {'msg': '400 Bad Request', 'errors': err.messages}, 400

        user = User.get_by_email(data.get('email'))
        if not user:
            return {'msg': 'E-mailadres is niet gelinkt aan een account'}, 403
        if user.is_activated:
            return {'msg': 'Account is reeds geactiveerd'}, 403

        user.set_password(data.get('password'))
        user.is_sharing = data.get('isSharing')
        db.session.add(user)
        db.session.commit()

        emails.send_activation(user)
        return {'success': True}, 200


@api.resource('/auth/reset')
class ResetResource(Resource):

    def post(self):
        json_data = request.get_json()
        try:
            data = reset_schema.load(json_data)
        except ma.ValidationError as err:
            return {'msg': '400 Bad Request', 'errors': err.messages}, 400

        user = User.get_by_email(data.get('email'))
        if not user:
            return {'msg': 'E-mailadres is niet gelinkt aan een account'}, 403
        if not user.is_activated:
            return {'msg': 'Activeer je account'}, 403

        emails.send_reset(user)
        return {'success': True}, 200
