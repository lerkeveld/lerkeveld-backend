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
class MaterialReservationListResource(Resource):

    @jwt.jwt_required
    def get(self):
        yesterday = datetime.date.today() - datetime.timedelta(1)
        reservations = MaterialReservation.get_all_after(yesterday)

        user = jwt.current_user
        for reservation in reservations:
            reservation.own = user.id == reservation.user.id

        data = reservations_schema.dump(reservations)
        return {'success': True, 'reservations': data}

    @jwt.jwt_required
    def post(self):
        json_data = request.get_json()
        try:
            data = reserve_schema.load(json_data)
        except ma.ValidationError as err:
            return {'msg': '400 Bad Request', 'errors': err.messages}, 400

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


@api.resource('/materiaal/<int:reservation_id>')
class MaterialReservationResource(Resource):

    @jwt.jwt_required
    def delete(self, reservation_id):
        user = jwt.current_user
        reservation = MaterialReservation.query.get(reservation_id)
        if not reservation or reservation.user.id != user.id:
            return {'msg': '400 Bad Request'}, 400

        db.session.delete(reservation)
        db.session.commit()
        return {'success': True}


@api.resource('/materiaal/type')
class MaterialTypeResource(Resource):

    @jwt.jwt_required
    def get(self):
        types = MaterialType.query.all()
        data = material_types_schema.dump(types)
        return {'success': True, 'items': data}
