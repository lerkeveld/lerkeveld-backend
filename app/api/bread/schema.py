from marshmallow import fields, ValidationError

from app import ma
from app.models import BreadType


def validate_not_none(value):
    """
    Validates whether the given value is None.
    """
    if value is None:
        raise ValidationError('Items contains an unknown bread type')


class OrderSchema(ma.Schema):
    id = fields.Integer()
    date = fields.Date()
    items = fields.Function(
        lambda user_order: list(map(lambda item: item.name, user_order.items))
    )
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


class BreadTypeSchema(ma.Schema):
    name = fields.String()
