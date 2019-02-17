import datetime

import flask_jwt_extended as jwt
from flask import request
from flask_restful import Resource

from app import db
from app.api import api
from app.models import BreadOrder, BreadType, BreadOrderDate
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
        orderdates = BreadOrderDate.get_all_after(startdate)

        for orderdate in orderdates:
            order = (BreadOrder.query
                     .filter(BreadOrder.bread_order_date == orderdate)
                     .filter(BreadOrder.user == user).first())
            if order is None:
                orderdate.items = []
            else:
                orderdate.items = list(order.items)

        data, _ = order_schema.dump(orderdates)
        return {'success': True, 'orders': data}


@api.resource('/bread/<int:order_date_id>')
class BreadDateResource(Resource):

    @jwt.jwt_required
    def patch(self, order_date_id):
        json_data = request.get_json()
        data, errors = breadlist_schema.load(json_data)
        if not data or errors:
            return {'msg': '400 Bad Request', 'errors': errors}, 400

        user = jwt.current_user
        order_date = BreadOrderDate.query.get(order_date_id)
        if not order_date or not order_date.is_editable:
            return {'msg': '400 Bad Request'}, 400

        order = BreadOrder.get_by_date_and_user(order_date, user)
        if order is None:
            order = BreadOrder(bread_order_date=order_date, user=user)

        order.items.append(*data.get('items'))
        db.session.add(order)
        db.session.commit()
        return {'success': True}

    @jwt.jwt_required
    def delete(self, order_date_id):
        user = jwt.current_user
        order_date = BreadOrderDate.query.get(order_date_id)
        if not order_date or not order_date.is_editable:
            return {'msg': '400 Bad Request'}, 400

        order = BreadOrder.get_by_date_and_user(order_date, user)
        if order is not None:
            db.session.delete(order)
            db.session.commit()
        return {'success': True}


@api.resource('/bread/type')
class BreadTypeResource(Resource):

    @jwt.jwt_required
    def get(self):
        types = BreadType.query.all()
        data, _ = bread_types_schema.dump(types)
        return {'success': True, 'items': data}
