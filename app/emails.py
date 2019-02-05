from flask import render_template, url_for
from flask_mail import Message

from app import app, mail
from app.decorators import async
from app.security import dump_token


@async
def send_async_email(msg):
    """
    Sends an email asynchronously.
    """
    with app.app_context():
        mail.send(msg)


def send_activation(user):
    """
    Send an email to the user to activate his account.
    """
    token = dump_token(user.email, salt='token-activate')
    secret_url = url_for(
        'token.activate', token=token, _external=True
    )

    msg = Message()
    msg.subject = 'Lerkeveld Underground - Activeer Account'
    msg.add_recipient(user.email)
    msg.body = render_template(
        'emails/activation.txt', user=user, secret_url=secret_url
    )
    msg.html = render_template(
        'emails/activation.html', user=user, secret_url=secret_url
    )
    send_async_email(msg)


def send_reset(user):
    """
    Send an email to the user to reset his password.
    """
    token = dump_token(user.email, salt='token-reset')
    secret_url = url_for(
        'token.reset', token=token, _external=True
    )

    msg = Message()
    msg.subject = 'Lerkeveld Underground - Reset Wachtwoord'
    msg.add_recipient(user.email)
    msg.body = render_template(
        'emails/reset.txt', user=user, secret_url=secret_url
    )
    msg.html = render_template(
        'emails/reset.html', user=user, secret_url=secret_url
    )
    send_async_email(msg)


def send_kotbar_reservation(reservation):
    """
    Sends an email to notify the user of a successful reservation of the kotbar.
    """
    msg = Message()
    msg.subject = 'Lerkeveld Underground - Bevestiging Reservatie'
    msg.add_recipient(reservation.user.email)
    msg.body = render_template(
        'emails/kotbar_reservation.txt', reservation=reservation
    )
    msg.html = render_template(
        'emails/kotbar_reservation.html', reservation=reservation
    )
    send_async_email(msg)


def send_kotbar_reservation_admin(reservation):
    """
    Sends an email to notify the kotbar mailinglist of a new successful
    reservation.
    """
    msg = Message()
    msg.subject = 'Lerkeveld Underground - Reservatie Kotbar'
    msg.recipients = app.config.get('MAIL_KOTBAR_ADMIN', [])
    msg.body = render_template(
        'emails/kotbar_reservation_admin.txt', reservation=reservation
    )
    msg.html = render_template(
        'emails/kotbar_reservation_admin.html', reservation=reservation
    )
    send_async_email(msg)


def send_materiaal_reservation(reservation):
    """
    Sends an email to notify the user of a successful reservation of material.
    """
    msg = Message()
    msg.subject = 'Lerkeveld Underground - Bevestiging Reservatie'
    msg.add_recipient(reservation.user.email)
    msg.body = render_template(
        'emails/materiaal_reservation.txt', reservation=reservation
    )
    msg.html = render_template(
        'emails/materiaal_reservation.html', reservation=reservation
    )
    send_async_email(msg)


def send_materiaal_reservation_admin(reservation):
    """
    Sends an email to notify the material mailinglist of a new successful
    reservation.
    """
    msg = Message()
    msg.subject = 'Lerkeveld Underground - Reservatie Materiaal'
    msg.recipients = app.config.get('MAIL_KOTBAR_ADMIN', [])
    msg.body = render_template(
        'emails/materiaal_reservation_admin.txt', reservation=reservation
    )
    msg.html = render_template(
        'emails/materiaal_reservation_admin.html', reservation=reservation
    )
    send_async_email(msg)
