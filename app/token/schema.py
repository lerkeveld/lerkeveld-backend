from marshmallow import fields
from marshmallow.validate import Length

from app import ma


class ResetSchema(ma.Schema):
    password = fields.String(required=True, validate=Length(8))
