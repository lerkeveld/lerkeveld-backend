from marshmallow import fields, ValidationError
import datetime

from app import ma
from app.models import KotbarReservation


def validate_date(date):
    min_date = datetime.date.today()
    max_date = min_date + datetime.timedelta(101)
    if not (min_date <= date <= max_date):
        raise ValidationError(
            f'Date should be between (and including) {min_date} and {max_date}.'
        )
    if KotbarReservation.is_booked(date):
        raise ValidationError('Date is already booked.')


class ReservationSchema(ma.Schema):
    id = fields.Integer()
    username = fields.Function(lambda reservation: reservation.user.fullname)
    date = fields.Date()
    description = fields.String()


class ReserveSchema(ma.Schema):
    date = fields.Date(required=True, validate=validate_date)
    description = fields.String(required=True)
