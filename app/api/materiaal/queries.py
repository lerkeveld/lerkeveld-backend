from app import db
from app.models import MaterialType, MaterialReservation, association_material_reservation_items


def get_items_booked_on_date(date):
    """
    Returns the material types booked on a given date.
    """
    query = db.session.query(MaterialType.id) \
        .join(association_material_reservation_items) \
        .join(MaterialReservation) \
        .filter(MaterialReservation.date == date)
    return list(map(lambda result: result[0], query.all()))
