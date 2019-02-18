from marshmallow import fields, ValidationError

from app import ma
from app.models import BreadType


def validate_not_none(value):
    """
    Validates whether the given value is None.
    """
    if value is None:
        raise ValidationError('Items contains an unknown bread type')


class BreadTypeSchema(ma.Schema):
    id = fields.Integer()
    name = fields.String()
    price = fields.Integer()


class BreadOrderSchema(ma.Schema):
    id = fields.Integer()
    type = fields.String()


class BreadOrderDates(ma.Schema):
    id = fields.Integer()
    date = fields.Date()
    is_active = fields.Boolean()
    is_editable = fields.Boolean()
    orders = fields.List(fields.Nested(BreadOrderSchema))
    total_price = fields.Integer()


class BreadOrderingSchema(ma.Schema):
    items = fields.List(
        fields.Function(
            deserialize=lambda item: BreadType.from_name(item),
            validate=validate_not_none
        ),
        required=True
    )
