from flask import render_template, url_for
from flask_mail import Message

from app import app, mail
from app.decorators import async
from app.security import dump_token


@async
def send_async_email(app, msg):
    """
    Sends an email asynchronously.
    """
    with app.app_context():
        mail.send(msg)


def send_email(subject, recipients, text_body, html_body, sender=None):
    """
    Convenience function to send an email with provided subject, recipients,
    text body, html body and optionally a sender.
    """
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    send_async_email(app, msg)


def send_activation(user):
    """
    Send an email to the user to activate his account.
    """
    token = dump_token(user.email, salt='token-activate')
    secret_url = url_for(
        'token.activate', token=token, _external=True
    )
    text_body = render_template(
        'emails/activation.txt', user=user, secret_url=secret_url
    )
    html_body = render_template(
        'emails/activation.html', user=user, secret_url=secret_url
    )
    send_email(
        'Lerkeveld Underground - Activeer Account',
        recipients=[user.email],
        text_body=text_body,
        html_body=html_body
    )

def send_reset(user):
    """
    Send an email to the user to reset his password.
    """
    token = dump_token(user.email, salt='token-reset')
    secret_url = url_for(
        'token.reset', token=token, _external=True
    )
    text_body = render_template(
        'emails/reset.txt', user=user, secret_url=secret_url
    )
    html_body = render_template(
        'emails/reset.html', user=user, secret_url=secret_url
    )
    send_email(
        'Lerkeveld Underground - Reset Wachtwoord',
        [user.email],
        text_body=text_body,
        html_body=html_body
    )
