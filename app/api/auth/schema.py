from marshmallow import fields
from marshmallow.validate import Length

from app import ma


class LoginSchema(ma.Schema):
    email = fields.String(required=True)
    password = fields.String(required=True)


class ActivateSchema(ma.Schema):
    email = fields.String(required=True)
    password = fields.String(required=True, validate=Length(8))


class ResetSchema(ma.Schema):
    email = fields.String(required=True)
