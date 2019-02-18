from app.models import BreadOrder, BreadOrderDate


def get_all_order_dates(user, after_date):
    """
    Returns for all order dates the orders of a user after a given date.
    """
    result = {}
    dates = BreadOrderDate.query \
                          .filter(BreadOrderDate.date > after_date) \
                          .all()
    for order_date in dates:
        result[order_date.id] = {
            'id': order_date.id,
            'date': order_date.date,
            'is_active': order_date.is_active,
            'is_editable': order_date.is_editable,
            'orders': [],
            'total_price': 0
        }

    items = BreadOrder.query \
                      .join(BreadOrderDate) \
                      .filter(BreadOrderDate.date > after_date) \
                      .filter(BreadOrder.user_id == user.id) \
                      .all()
    for item in items:
        if item.date.id not in result:
            continue
        data = result[item.date.id]
        data['orders'].append({
            'id': item.id,
            'type': item.type.name
        })
        data['total_price'] += item.type.price
    return result.values()
