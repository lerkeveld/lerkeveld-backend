from app import db
from app.models import BreadOrder, BreadOrderDate
from sqlalchemy import text


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
    query = text(""" select u.first_name, u.last_name, u.corridor, u.room,
                 bt.name from bread_order_date as bod
                 join bread_order as bo on bod.id = bo.date_id
                 join user as u on bo.user_id = u.id
                 join bread_type as bt on bo.type_id = bt.id
                 where bod.id = :date
                 order by u.corridor, u.room asc""")
    return db.session.execute(query, {"date": date.id})


def get_week_order_totals(date):
    """
    Get the totals for the order for a certain week.
    """
    query = text("""select bt.id, bt.name, count(bod.id)
                 from bread_order_date as bod
                 join bread_order as bo on bod.id = bo.date_id
                 join bread_type as bt on bo.type_id = bt.id
                 where bod.id = :date
                 group by(bt.id)
                 order by bt.id""")
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
