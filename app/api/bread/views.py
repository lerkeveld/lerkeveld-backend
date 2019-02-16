import datetime

import flask_jwt_extended as jwt
from flask import request
from flask_restful import Resource

from app import db
from app.api import api
from app.models import BreadOrder, BreadType
from .schema import OrderSchema, BreadListSchema, BreadTypeSchema

order_schema = OrderSchema(many=True)
breadlist_schema = BreadListSchema()
bread_types_schema = BreadTypeSchema(many=True)


@api.resource('/bread/')
class BreadOrderListResource(Resource):

    @jwt.jwt_required
    def get(self):
        startdate = datetime.date.today()
        if startdate.month >= 9:
            startdate = startdate.replace(month=9, day=1)
        else:
            startdate = startdate.replace(month=1, day=1)

        user = jwt.current_user
        orders = BreadOrder.get_all_after_user(startdate, user)

        for order in orders:
            order.date = order.bread_date.date

        data, _ = order_schema.dump(orders)
        return {'success': True, 'orders': data}

    @jwt.jwt_required
    def post(self):
        json_data = request.get_json()
        data, errors = breadlist_schema.load(json_data)
        if not data or errors:
            return {'msg': '400 Bad Request', 'errors': errors}, 400

        user = jwt.current_user

        reservation = BreadOrder(
            user=user,
            date=data.get('date'),
            items=data.get('items')
        )
        db.session.add(reservation)
        db.session.commit()

        return {'success': True}


@api.resource('/bread/<int:order_id>')
class BreadOrderResource(Resource):

    @jwt.jwt_required
    def put(self, order_id):
        json_data = request.get_json()
        data, errors = breadlist_schema.load(json_data)
        if not data or errors:
            return {'msg': '400 Bad Request', 'errors': errors}, 400

        user = jwt.current_user
        order = BreadOrder.query.get(order_id)
        if not order or not order.editable or order.user.id != user.id:
            return {'msg': '400 Bad Request'}, 400

        order.items = data.get('items')
        db.session.commit()
        return {'success': True}

    @jwt.jwt_required
    def patch(self, order_id):
        json_data = request.get_json()
        data, errors = breadlist_schema.load(json_data)
        if not data or errors:
            return {'msg': '400 Bad Request', 'errors': errors}, 400

        user = jwt.current_user
        order = BreadOrder.query.get(order_id)
        if not order or not order.editable or order.user.id != user.id:
            return {'msg': '400 Bad Request'}, 400

        order.items.append(data.get('items'))
        db.session.commit()
        return {'success': True}


@api.resource('/bread/type')
class BreadTypeResource(Resource):

    @jwt.jwt_required
    def get(self):
        types = BreadType.query.all()
        data, _ = bread_types_schema.dump(types)
        return {'success': True, 'items': data}
