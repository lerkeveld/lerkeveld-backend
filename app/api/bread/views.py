import datetime

import flask_jwt_extended as jwt
from flask import request
from flask_restful import Resource

from app import db
from app.api import api
from app.models import BreadOrder, BreadType, BreadOrderDate
from .queries import get_all_order_dates
from .schema import BreadOrderDates, BreadOrderingSchema, BreadTypeSchema

bread_order_dates_schema = BreadOrderDates(many=True)
bread_ordering_schema = BreadOrderingSchema()
bread_types_schema = BreadTypeSchema(many=True)


@api.resource('/bread/')
class BreadOrderDateListResource(Resource):

    @jwt.jwt_required
    def get(self):
        # TODO: solve start_date hack
        start_date = datetime.date.today()
        if start_date.month >= 9:
            start_date = start_date.replace(month=9, day=1)
        else:
            start_date = start_date.replace(month=1, day=1)

        user = jwt.current_user
        order_dates = get_all_order_dates(user, start_date)

        data, _ = bread_order_dates_schema.dump(order_dates)
        return {'success': True, 'order_dates': data}


@api.resource('/bread/<int:order_date_id>')
class BreadOrderDateResource(Resource):

    @jwt.jwt_required
    def patch(self, order_date_id):
        order_date = BreadOrderDate.query.get(order_date_id)
        if not order_date:
            return {'msg': 'Order date not found'}, 400
        if not order_date.is_editable:
            return {'msg': 'Order date not editable'}, 400

        json_data = request.get_json()
        data, errors = bread_ordering_schema.load(json_data)
        if not data or errors:
            return {'msg': '400 Bad Request', 'errors': errors}, 400

        user = jwt.current_user
        for item in data.get('items'):
            order = BreadOrder(
                user=user,
                date=order_date,
                type=item
            )
            db.session.add(order)
        db.session.commit()
        return {'success': True}

    @jwt.jwt_required
    def delete(self, order_date_id):
        order_date = BreadOrderDate.query.get(order_date_id)
        if not order_date:
            return {'msg': 'Order date not found'}, 400
        if not order_date.is_editable:
            return {'msg': 'Order date not editable'}, 400

        user = jwt.current_user
        db.session.query(BreadOrder).filter(
            BreadOrder.user_id == user.id,
            BreadOrder.date_id == order_date_id
        ).delete()
        db.session.commit()
        return {'success': True}


@api.resource('/bread/type')
class BreadTypeResource(Resource):

    @jwt.jwt_required
    def get(self):
        types = BreadType.query.all()
        data, _ = bread_types_schema.dump(types)
        return {'success': True, 'items': data}
