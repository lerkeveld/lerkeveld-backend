import sqlalchemy as sqla

from app import db
from app.models import BreadOrder, BreadOrderDate


def get_order_dates(after_date):
    """
    Returns the order dates occurring after the given date.
    """
    query = BreadOrderDate.query \
                          .filter(BreadOrderDate.date > after_date)
    return query.all()


def get_orders(user, after_date):
    """
    Returns all orders for the given user occurring after the given date.
    """
    query = BreadOrder.query \
                      .join(BreadOrderDate) \
                      .filter(BreadOrderDate.date > after_date) \
                      .filter(BreadOrder.user_id == user.id)
    return query.all()


def get_order_dates_extended(user, after_date):
    """
    Returns for all order dates the orders of a user after a given date.
    """
    result = {}
    dates = get_order_dates(after_date)
    for order_date in dates:
        result[order_date.id] = {
            'id': order_date.id,
            'date': order_date.date,
            'is_active': order_date.is_active,
            'is_editable': order_date.is_editable,
            'orders': [],
            'total_price': 0
        }

    orders = get_orders(user, after_date)
    for order in orders:
        if order.date.id not in result:
            continue
        data = result[order.date.id]
        data['orders'].append({
            'id': order.id,
            'type': order.type.name
        })
        data['total_price'] += order.type.price
    return result.values()


def get_week_order_detailed(date):
    """
    Get all user orders for a certain week.
    """
    query = sqla.text("""
        SELECT "user".first_name, "user".last_name, "user".corridor, "user".room, bt.name
        FROM bread_order_date AS bod
        JOIN bread_order AS bo ON bod.id = bo.date_id
        JOIN "user" ON bo.user_id = "user".id
        JOIN bread_type bt ON bo.type_id = bt.id
        WHERE bod.id = :date
        ORDER BY "user".corridor, "user".room asc
    """)
    return db.session.execute(query, {"date": date.id})


def get_week_order_totals(date):
    """
    Get the totals for the order for a certain week.
    """
    query = sqla.text("""
        SELECT bt.id, bt.name, COUNT(bod.id)
        FROM bread_order_date AS bod
        JOIN bread_order AS bo ON bod.id = bo.date_id
        JOIN bread_type AS bt ON bo.type_id = bt.id
        WHERE bod.id = :date
        GROUP BY(bt.id)
        ORDER BY bt.id
    """)
    return db.session.execute(query, {"date": date.id})


def add_orders_on(user, order_date, items):
    """
    Adds for a user all orders specified by items on the specified date.
    """
    for item in items:
        order = BreadOrder(
            user=user,
            date=order_date,
            type=item
        )
        db.session.add(order)
    db.session.commit()


def add_orders_after(user, after_date, items):
    """
    Adds for a user all orders specified by items on all editable order dates
    after the specified date.
    """
    order_dates = get_order_dates(after_date)
    for order_date in order_dates:
        if not order_date.is_editable:
            continue

        for item in items:
            order = BreadOrder(
                user=user,
                date=order_date,
                type=item
            )
            db.session.add(order)
    db.session.commit()


def delete_orders_on(user, order_date):
    """
    Deletes for a user all orders on the specified date.
    """
    db.session.query(BreadOrder).filter(
        BreadOrder.user_id == user.id,
        BreadOrder.date_id == order_date.id
    ).delete()
    db.session.commit()


def delete_orders_after(user, after_date):
    """
    Deletes for a user all editable orders after the specified date.
    """
    orders = get_orders(user, after_date)
    for order in orders:
        if not order.date.is_editable:
            continue

        db.session.delete(order)
    db.session.commit()
