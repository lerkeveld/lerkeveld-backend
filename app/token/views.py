import datetime
import marshmallow as ma

from flask import render_template, request, abort
from itsdangerous import BadData, SignatureExpired

from app import app, db
from app.models import User, KotbarReservation, BreadOrderDate
from app.security import load_token
from app.token import token_blueprint
from app.api.bread.queries import (
        get_week_order_detailed,
        get_week_order_totals
     )
from .schema import ResetSchema

reset_schema = ResetSchema()


@token_blueprint.route('/activate/<token>', methods=['GET'])
def activate(token):
    """
    A view which activates the user identified by provided token.
    """
    try:
        email = load_token(token, salt='token-activate')
    except SignatureExpired:
        return render_template('token/timeout.html')
    except BadData:
        return render_template('token/failure.html')

    user = User.get_by_email(email)
    if not user:
        return render_template('token/failure.html')

    user.is_activated = True
    db.session.add(user)
    db.session.commit()
    return render_template('token/activation.html')


@token_blueprint.route('/reset/<token>', methods=['GET', 'POST'])
def reset(token):
    """
    A view which presents the user with a form to input a password. If the user
    inputs a password, his password is reset.
    """
    try:
        email = load_token(token, salt='token-reset')
    except SignatureExpired:
        return render_template('token/timeout.html')
    except BadData:
        return render_template('token/failure.html')

    user = User.get_by_email(email)
    if not user:
        return render_template('token/failure.html')

    errors = {}
    if request.method == 'POST':
        request_data = request.form
        try:
            data = reset_schema.load(request_data)
            user.set_password(data.get('password'))
            db.session.add(user)
            db.session.commit()
            return render_template('token/reset_success.html')
        except ma.ValidationError as err:
            errors = err.messages

    return render_template('token/reset.html', token=token, errors=errors)


@token_blueprint.route('/kotbar_reservations/<token>', methods=['GET'])
def kotbar_reservations(token):
    """
    A view which presents the user with the coming kotbar reservations.
    """
    if token != app.config.get('TOKEN_KOTBAR_RESERVATIONS', None):
        return render_template('token/failure.html')

    yesterday = datetime.date.today() - datetime.timedelta(1)
    reservations = KotbarReservation.get_all_after(yesterday)
    reservations = sorted(reservations, key=lambda r: r.date)

    return render_template(
        'token/kotbar_reservations.html',
        reservations=reservations
    )


@token_blueprint.route('/bread_reservations/<token>', methods=['GET'])
def bread_reservations(token):
    """
    A view which presents the user with the current bread reservations.
    """
    if token != app.config.get('TOKEN_BREAD_RESERVATIONS', None):
        return render_template('token/failure.html')

    reservations = BreadOrderDate.query.all()
    reservations = sorted(reservations, key=lambda r: r.date)

    return render_template(
        'bread/bread_reservations.html',
        reservations=reservations,
        token=token
    )


@token_blueprint.route('/bread_reservation/<int:odi>/<token>', methods=['GET'])
def bread_reservation(token, odi):
    """
    A view which presents the user with the bread reservation of a week.
    """
    if token != app.config.get('TOKEN_BREAD_RESERVATIONS', None):
        return render_template('token/failure.html')

    order_date = BreadOrderDate.query.get(odi)
    if not order_date:
        return abort(404)

    # These are iterators, they only yield their results once
    orders = get_week_order_detailed(order_date)
    totals = get_week_order_totals(order_date)

    return render_template(
        'bread/bread_reservation_week.html',
        orders=orders,
        totals=totals
    )
