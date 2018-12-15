# lerkeveld-backend
Backend of the Lerkeveld website, providing an api to the Lerkeveld Underground application (see https://github.com/lerkeveld/lerkeveld-underground).

## Development
Installation requirements:
- python3
- virtualenv

Installation instructions:

```bash
git clone 'https://github.com/lerkeveld/lerkeveld-backend' .
cd lerkeveld-backend
virtualenv --python=python3 env
./env/bin/pip install -r requirements.txt
touch secret.py
```

Add following **development** configuration options to secret.py:
(Optionally, add your own email account, see https://stackoverflow.com/questions/37058567/configure-flask-mail-to-use-gmail)

```python
# flask
SECRET_KEY = 'secret'

# flask_jwt_extended
JWT_SECRET_KEY = 'secret'

# flask_cors
CORS_ORIGINS = ['http://localhost:3000']

# flask_mail (optional)
```

Add a user to the database using a python terminal (from the repository root execute `env/bin/python`):
```python
from app import db
from app.models import User
db.create_all()
user = User(
    first_name="Test",
    last_name="Test",
    email="test.test@domain.com",
    password="lerkeveld"
)
db.session.add(user)
db.session.commit()
```

## Production
TODO