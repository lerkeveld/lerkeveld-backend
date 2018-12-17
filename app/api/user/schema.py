from marshmallow import fields
from marshmallow.validate import Length

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


class EditSchema(ma.Schema):
    is_sharing = fields.Boolean()


class EditSecureSchema(ma.Schema):
    check = fields.String(required=True)
    email = fields.Email()
    password = fields.String(validate=Length(8))
