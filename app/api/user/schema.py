from marshmallow import fields

from app import ma


class UserSchema(ma.Schema):
    first_name = fields.String()
    last_name = fields.String()
    email = fields.Email()
    phone = fields.String()
    corridor = fields.String()
    room = fields.Integer()
    is_sharing = fields.Boolean()
    is_member = fields.Boolean()
