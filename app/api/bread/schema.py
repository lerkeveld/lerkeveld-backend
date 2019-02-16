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
    name = fields.String()
    price = fields.Integer()


class OrderSchema(ma.Schema):
    id = fields.Integer()
    date = fields.Date()
    items = fields.List(fields.Nested(BreadTypeSchema))
    is_active = fields.Boolean()
    is_editable = fields.Boolean()


class BreadListSchema(ma.Schema):
    items = fields.List(
        fields.Function(
            deserialize=lambda item: BreadType.from_name(item),
            validate=validate_not_none
        ),
        required=True
    )
