import datetime

import flask_jwt_extended as jwt
from flask import request
from flask_restful import Resource

from app import db
from app import emails
from app.api import api
from app.models import MaterialReservation, MaterialType
from .schema import ReservationSchema, ReserveSchema, MaterialTypeSchema

reservations_schema = ReservationSchema(many=True)
reserve_schema = ReserveSchema()
material_types_schema = MaterialTypeSchema(many=True)


@api.resource('/materiaal/')
class MaterialResource(Resource):

    @jwt.jwt_required
    def get(self):
        yesterday = datetime.date.today() - datetime.timedelta(1)
        reservations = MaterialReservation.get_all_after(yesterday)
        data, _ = reservations_schema.dump(reservations)
        return {'success': True, 'reservations': data}

    @jwt.jwt_required
    def post(self):
        json_data = request.get_json()
        data, errors = reserve_schema.load(json_data)
        if not data or errors:
            return {'msg': '400 Bad Request', 'errors': errors}, 400

        user = jwt.current_user

        reservation = MaterialReservation(
            user=user,
            date=data.get('date'),
            items=data.get('items')
        )
        db.session.add(reservation)
        db.session.commit()

        emails.send_materiaal_reservation(reservation)
        emails.send_materiaal_reservation_admin(reservation)
        return {'success': True}


@api.resource('/materiaal/type')
class MaterialTypeResource(Resource):

    @jwt.jwt_required
    def get(self):
        types = MaterialType.query.all()
        data, _ = material_types_schema.dump(types)
        return {'success': True, 'items': data}
