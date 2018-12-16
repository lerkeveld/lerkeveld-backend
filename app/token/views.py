from flask import render_template
from itsdangerous import BadData, SignatureExpired

from app import db
from app.models import User
from app.security import load_token
from app.token import token_blueprint


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
