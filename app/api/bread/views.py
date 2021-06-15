import datetime
import marshmallow as ma

import flask_jwt_extended as jwt
from flask import request
from flask_restful import Resource

from app.api import api
from app.models import BreadType, BreadOrderDate
from . import queries
from .schema import BreadOrderDates, BreadOrderingSchema, BreadTypeSchema

bread_order_dates_schema = BreadOrderDates(many=True)
bread_ordering_schema = BreadOrderingSchema()
bread_types_schema = BreadTypeSchema(many=True)


def get_start_date():
    # TODO: solve start_date hack
    start_date = datetime.date.today()
    if start_date.month >= 9:
        start_date = start_date.replace(month=9, day=1)
    else:
        start_date = start_date.replace(month=1, day=1)
    return start_date


@api.resource('/bread/')
class BreadOrderDateListResource(Resource):

    @jwt.jwt_required()
    def get(self):
        user = jwt.current_user
        start_date = get_start_date()
        order_dates = queries.get_order_dates_extended(user, start_date)
        data = bread_order_dates_schema.dump(order_dates)
        return {'success': True, 'order_dates': data}


@api.resource('/bread/<int:order_date_id>')
class BreadOrderDateResource(Resource):

    @jwt.jwt_required()
    def patch(self, order_date_id):
        order_date = BreadOrderDate.query.get(order_date_id)
        if not order_date:
            return {'msg': 'Order date not found'}, 400
        if not order_date.is_editable:
            return {'msg': 'Order date not editable'}, 400

        json_data = request.get_json()
        try:
            data = bread_ordering_schema.load(json_data)
        except ma.ValidationError as err:
            return {'msg': '400 Bad Request', 'errors': err.messages}, 400

        user = jwt.current_user
        queries.add_orders_on(user, order_date, data.get('items'))
        return {'success': True}

    @jwt.jwt_required()
    def delete(self, order_date_id):
        order_date = BreadOrderDate.query.get(order_date_id)
        if not order_date:
            return {'msg': 'Order date not found'}, 400
        if not order_date.is_editable:
            return {'msg': 'Order date not editable'}, 400

        user = jwt.current_user
        queries.delete_orders_on(user, order_date)
        return {'success': True}


@api.resource('/bread/all')
class BreadAllOrderDatesResource(Resource):

    @jwt.jwt_required()
    def patch(self):
        json_data = request.get_json()
        try:
            data = bread_ordering_schema.load(json_data)
        except ma.ValidationError as err:
            return {'msg': '400 Bad Request', 'errors': err.messages}, 400

        user = jwt.current_user
        start_date = get_start_date()
        queries.add_orders_after(user, start_date, data.get('items'))
        return {'success': True}

    @jwt.jwt_required()
    def delete(self):
        user = jwt.current_user
        start_date = get_start_date()
        queries.delete_orders_after(user, start_date)
        return {'success': True}


@api.resource('/bread/type')
class BreadTypeResource(Resource):

    @jwt.jwt_required()
    def get(self):
        types = BreadType.query.all()
        data = bread_types_schema.dump(types)
        return {'success': True, 'items': data}
