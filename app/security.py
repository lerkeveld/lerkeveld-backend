import argon2
import secrets
import string
from itsdangerous import URLSafeTimedSerializer

from app import app


def generate_random_password(N):
    """
    Generates a random password of given length.
    """
    return ''.join(
        secrets.choice(string.ascii_letters + string.digits) for _ in range(N)
    )


def generate_password_hash(password):
    """
    Hash a password with the argon2 key derivation function.
    """
    password_hasher = argon2.PasswordHasher(hash_len=32)
    return password_hasher.hash(password)


def check_password_hash(password_hash, password):
    """
    Check a password against a given hashed password value.
    """
    password_hasher = argon2.PasswordHasher(hash_len=32)
    try:
        return password_hasher.verify(password_hash, password)
    except argon2.exceptions.VerificationError:
        return False


def dump_token(obj, salt):
    """
    Returns the url safe signed object with given salt and time of creation
    included.
    """
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(obj, salt=salt)


def load_token(token, salt=None):
    """
    Returns the object included in the token. Also verifies the signature of the
    token.
    """
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.loads(
        token,
        salt=salt,
        max_age=app.config['TOKEN_MAX_AGE']
    )
