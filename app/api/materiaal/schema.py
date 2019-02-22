from marshmallow import fields, ValidationError, validates_schema

from app import ma
from app.models import MaterialType
from .queries import get_items_booked_on_date


def validate_not_none(value):
    """
    Validates whether the given value is None.
    """
    if value is None:
        raise ValidationError('Items contains an unknown material type')


def validate_distinct(lst):
    """
    Validates whether the given list contains duplicate entries.
    """
    if len(lst) != len(set(lst)):
        raise ValidationError('Items contains duplicate entries')


class ReservationSchema(ma.Schema):
    id = fields.Integer()
    username = fields.Function(lambda reservation: reservation.user.fullname)
    date = fields.Date()
    items = fields.Function(
        lambda reservation: list(map(lambda item: {
            'id': item.id,
            'name': item.name
        }, reservation.items))
    )
    own = fields.Boolean()


class ReserveSchema(ma.Schema):
    date = fields.Date(required=True)
    items = fields.List(
        fields.Function(
            deserialize=lambda item: MaterialType.query.get(item),
            validate=validate_not_none
        ),
        required=True,
        validate=validate_distinct
    )

    @validates_schema
    def validate_schema(self, data):
        """
        Validates this schema on duplicate bookings.
        """
        booked_items = set(get_items_booked_on_date(data.get('date')))
        for item in data.get('items'):
            if item and item.name in booked_items:
                raise ValidationError('Items contains a previously booked item')


class MaterialTypeSchema(ma.Schema):
    id = fields.Integer()
    name = fields.String()
