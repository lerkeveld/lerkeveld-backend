from flask import render_template, request, abort
from itsdangerous import BadData, SignatureExpired

from app import db
from app.models import User
from app.security import load_token
from app.token import token_blueprint
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

    if request.method == 'POST':
        request_data = request.form
        print(request.form)
        data, errors = reset_schema.load(request_data)
        if data and not errors:
            user.set_password(data.get('password'))
            db.session.add(user)
            db.session.commit()
            return render_template('token/reset_success.html')
        return abort(400)

    return render_template('token/reset.html', token=token)
