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
```python
import os
basedir = os.path.abspath(os.path.dirname(__file__))

# flask
SECRET_KEY = 'secret'

# flask_sqlalchemy
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')

# flask_jwt_extended
JWT_SECRET_KEY = 'secret'

# flask_cors
CORS_ORIGINS = ['http://localhost:3000']
CORS_SUPPORTS_CREDENTIALS = True

# flask_mail
# MAIL_SUPPRESS_SEND = False

# mailinglist
MAIL_KOTBAR_ADMIN = []
MAIL_MATERIAAL_ADMIN = []
```
Some optional configuration changes:
- Add your private IP address to `CORS_ORIGINS` to allow devices on your LAN to connect via the development version of the Lerkeveld Underground application.
- Add an email account (see https://stackoverflow.com/questions/37058567/configure-flask-mail-to-use-gmail) and uncomment the line with `MAIL_SUPPRESS_SEND`.
- Add your email address to `MAIL_KOTBAR_ADMIN` and `MAIL_MATERIAAL_ADMIN`.

### Setup the database
For **development**, by default a SQLite database placed at the repositories root is used (see configuration).
Create the database (from the repository root execute `env/bin/python`):
```python
from app import db
db.create_all()
```

### Initialize the database

#### Adding users
Add users to the database using a python shell (from the repository root execute `env/bin/python`):
```python
from app import db
from app.models import User
user = User(
    first_name="Test",
    last_name="Test",
    email="test.test@domain.com",
    room=0,
    corridor="N0"
)
db.session.add(user)
db.session.commit()
```

#### Adding material
Add users to the database using a python shell (from the repository root execute `env/bin/python`):
```python
from app import db
from app.models import MaterialType
material1 = MaterialType(name='Beamer')
material2 = MaterialType(name='BBQ 1')
material3 = MaterialType(name='BBQ 2')
db.session.add(material1)
db.session.add(material2)
db.session.add(material3)
db.session.commit()
```

## Production (Apache)
Installation requirements:
- apache (with `mod_fcgi` enabled)
- python3
- virtualenv

Installation instructions:
```bash
git clone 'https://github.com/lerkeveld/lerkeveld-backend' .
cd lerkeveld-backend
virtualenv --python=python3 ~/.env
~/.env/bin/pip install -r requirements.txt
touch secret.py
```

Add following **production** configuration options to secret.py:
```python
# flask
SECRET_KEY =

# flask_sqlalchemy
SQLALCHEMY_DATABASE_URI =

# flask_jwt_extended
JWT_SECRET_KEY =

# flask_cors
CORS_ORIGINS = []

# flask_mail
# MAIL_SUPPRESS_SEND = False

# mailinglist
MAIL_KOTBAR_ADMIN = []
MAIL_MATERIAAL_ADMIN = []
```
**Critical** configuration changes:
- Change `SECRET_KEY` and `JWT_SECRET_KEY` (the web server errors otherwise)
- Change `SQLALCHEMY_DATABASE_URI` (see later)
- Add to `CORS_ORIGINS` the domain name (with protocol, e.g. https://lerkies.simonbos.me) or IP address of the webserver hosting the frontend.
- Add an email account (see https://stackoverflow.com/questions/37058567/configure-flask-mail-to-use-gmail) and uncomment the line with `MAIL_SUPPRESS_SEND`.
- Add the relevant email addresses to `MAIL_KOTBAR_ADMIN` and `MAIL_MATERIAAL_ADMIN`. Note: everytime this configuration changes, the webserver has to restart. As such, it is best practice to use editable email forwarders here.

### Setup the database

#### PostgreSQL setup (recommended)
TODO

#### SQLite setup (not recommended)
Installation instructions (**requires root priviliges**):

1. Create a directory (`$DATA_DIR`) in which the sqlite database will be stored. **Do not put this in the web root.**
```bash
mkdir "$DATA_DIR"
```
2. Change the group of the `$DATA_DIR` directory to `www-data`:
```bash
sudo chgrp www-data "$DATA_DIR"
```
3. Change the permissions of the `$DATA_DIR` directory:
```bash
chmod g=rwx "$DATA_DIR"
```
4. Change `SQLALCHEMY_DATABASE_URI` in `config.py` to `sqlite:///$DATA_DIR/app.db`.
5. Create the database using following script from a python shell:
```python
from app import db
db.create_all()
```
6. Change the group of the database to `www-data`:
```bash
sudo chgrp www-data "$DATA_DIR/app.db"
```
7. Change the permissions of the database:
```bash
chmod g=rw "$DATA_DIR/app.db"
```

### Initialize the database
(see development)

### Connect backend to the web root
0. Enable `mod_fcgi`:
```bash
sudo a2enmod mod_fcgi
```

1. Install python-flup6:
```bash
~/.env/bin/pip install flup6
```

2. Add the file `app.fcgi` to the webroot:
```python
#!/home/user/.env/bin/python
import sys, os, os.path
from threading import Thread

this_file = os.path.realpath(__file__)

site_dir = '/home/user/lerkeveld-backend'
sys.path.insert(0, site_dir)
os.chdir(site_dir)

from flup.server.fcgi import WSGIServer
from app import app

def stat_thread():
    import time, os, signal
    start_mtime = os.stat(this_file).st_mtime
    while True:
        cur_mtime = os.stat(this_file).st_mtime
        if cur_mtime != start_mtime:
            os.kill(os.getpid(), signal.SIGTERM)
        time.sleep(1)

Thread(target=stat_thread).start()


class ScriptNameStripper(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        environ['SCRIPT_NAME'] = ''
        return self.app(environ, start_response)

app = ScriptNameStripper(app)

if __name__ == '__main__':
     WSGIServer(app).run()
```

**Critical** changes to the provided `app.fcgi` file:
- Change the absolute path of the shebang to the absolute path of the python interpreter of the virtual environment.
- Change `site_dir` to the absolute path of the `lerkeveld-backend` directory.

3. Add following lines to the .htaccess file at the webroot:
```.htaccess
Options +ExecCGI
AddHandler fcgid-script .fcgi

RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteRule ^admin/(.*)$ app.fcgi/admin/$1 [QSA,L]
RewriteRule ^api/(.*)$ app.fcgi/api/$1 [QSA,L]
RewriteRule ^token/(.*)$ app.fcgi/token/$1 [QSA,L]
```
