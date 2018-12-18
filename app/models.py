import sqlalchemy.sql as sql

from app import db
from app.security import (
    generate_password_hash, check_password_hash, generate_random_password
)

association_user_group = db.Table('association_user_group', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
)


class User(db.Model):

    """
    Represents a database model of a user.
    """

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)

    # General user info
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    phone = db.Column(db.String(16))
    corridor = db.Column(db.String(4))
    room = db.Column(db.Integer)

    # User capabilities
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    is_activated = db.Column(db.Boolean, nullable=False, default=False)
    is_sharing = db.Column(db.Boolean, nullable=False, default=False)
    is_member = db.Column(db.Boolean, default=None)

    # Secret user info
    password_hash = db.Column(db.String(128), nullable=False)

    groups = db.relationship('Group', secondary=association_user_group)

    def __init__(self, password=None, email=None, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        if password is None:
            password = generate_random_password(64)
        self.set_password(password)
        self.set_email(email)

    def __repr__(self):
        return f'<User {self.first_name} {self.last_name}>'

    @property
    def fullname(self):
        """
        Returns the full name of this user.
        """
        return f'{self.first_name} {self.last_name}'

    def set_password(self, password):
        """
        Generate a hash of the given plaintext password and set as password hash
        of this user.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Check the given plaintext password with the stored password hash.
        """
        return check_password_hash(self.password_hash, password)

    def set_email(self, email):
        """
        Set the email of this user to the given email in lower case.
        """
        self.email = email.lower()

    def has_email(self, email):
        """
        Returns whether this user has as it's stored email the given email in
        lower case.
        """
        return self.email == email.lower()

    def in_group(self, group):
        """
        Returns whether this user is in the given group.
        """
        qry = db.session.query(User.id)\
            .join(Group)\
            .filter(User.id == self.id, Group.name == group)
        return db.session.query(qry.exists()).scalar()

    @classmethod
    def get_by_email(cls, email):
        """
        Returns the User associated with the given email in lower case.
        """
        return cls.query.filter_by(email=email.lower()).first()

    @classmethod
    def get_by_fullname(cls, first_name, last_name):
        """
        Returns the User(s) associated with the given first_name
        and last_name.
        """
        return cls.query.filter_by(
            first_name=first_name,
            last_name=last_name
        ).first()

    @classmethod
    def email_exists(cls, email):
        """
        Returns whether a User with given email in lower case is registered.
        """
        return db.session.query(
            sql.exists().where(cls.email == email.lower())
        ).scalar()


class Group(db.Model):
    """
    Represents a database model of a group.
    """

    __tablename__ = 'group'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)

    def __repr__(self):
        return f'<Group {self.name}>'


class KotbarReservation(db.Model):

    """
    Represents a database model of a reservation of the kotbar.
    """

    __tablename__ = 'kotbar_reservation'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String, nullable=False)

    user = db.relationship('User')

    @classmethod
    def get_all_between(cls, start_date, end_date):
        """
        Returns all kotbar reservations between the given start date and end
        date.
        """
        return cls.query.filter(
            cls.date.between(start_date, end_date)
        ).order_by(sql.desc(cls.date)).all()

    @classmethod
    def get_all_after(cls, start_date):
        """
        Returns all kotbar reservations after the given start date.
        """
        return cls.query.filter(
            cls.date > start_date
        ).order_by(sql.desc(cls.date)).all()

    @classmethod
    def is_booked(cls, date):
        """
        Returns whether a reservation at the given date has been made.
        """
        return db.session.query(
            sql.exists()
               .where(cls.date == date)
        ).scalar()

