import datetime

import flask_jwt_extended as jwt
from flask import request
from flask_restful import Resource

from app import db
from app import emails
from app.api import api
from app.models import KotbarReservation
from .schema import ReservationSchema, ReserveSchema

reservations_schema = ReservationSchema(many=True)
reserve_schema = ReserveSchema()


@api.resource('/kotbar/')
class KotbarResource(Resource):

    @jwt.jwt_required
    def get(self):
        yesterday = datetime.date.today() - datetime.timedelta(1)
        reservations = KotbarReservation.get_all_after(yesterday)
        data, _ = reservations_schema.dump(reservations)
        return {'success': True, 'reservations': data}

    @jwt.jwt_required
    def post(self):
        json_data = request.get_json()
        data, errors = reserve_schema.load(json_data)
        if not data or errors:
            return {'msg': '400 Bad Request', 'errors': errors}, 400

        user = jwt.current_user

        reservation = KotbarReservation(
            user_id=user.id,
            date=data.get('date'),
            description=data.get('description')
        )
        db.session.add(reservation)
        db.session.commit()

        emails.send_kotbar_reservation(reservation)
        emails.send_kotbar_reservation_admin(reservation)
        return {'success': True}
