from marshmallow import fields

from app import ma


class LoginSchema(ma.Schema):
    email = fields.String(required=True)
    password = fields.String(required=True)
