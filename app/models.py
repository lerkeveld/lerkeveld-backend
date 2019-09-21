import sqlalchemy.sql as sql
import datetime

from sqlalchemy.ext.associationproxy import association_proxy

from app import db
from app.security import (
    generate_password_hash, check_password_hash, generate_random_password
)

association_user_group = db.Table(
    'association_user_group',
    db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
)

association_material_reservation_items = db.Table(
    'association_material_type',
    db.Model.metadata,
    db.Column('reservation_id', db.Integer, db.ForeignKey('material_reservation.id')),
    db.Column('type_id', db.Integer, db.ForeignKey('material_type.id'))
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
    phone = db.Column(db.String(16), default=None)
    corridor = db.Column(db.String(4), default=None)
    room = db.Column(db.String(8), default=None)

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
        return '<User {}>'.format(self.fullname)

    @property
    def fullname(self):
        """
        Returns the full name of this user.
        """
        return '{} {}'.format(self.first_name, self.last_name)

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
        return '<Group {}>'.format(self.name)


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


class MaterialReservation(db.Model):

    __tablename__ = 'material_reservation'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.Date, nullable=False)

    user = db.relationship('User')
    items = db.relationship(
        'MaterialType', secondary=association_material_reservation_items
    )

    def __repr__(self):
        return '<MaterialReservation by {} on {}>'.format(
            self.user.fullname, self.date
        )

    @classmethod
    def get_all_after(cls, start_date):
        """
        Returns all material reservations after the given start date.
        """
        return cls.query.filter(
            cls.date > start_date
        ).order_by(sql.desc(cls.date)).all()


class MaterialType(db.Model):

    __tablename__ = 'material_type'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    def __repr__(self):
        return '<MaterialType {}>'.format(self.name)

    @classmethod
    def from_name(cls, name):
        return cls.query.filter_by(name=name).first()


class BreadOrder(db.Model):

    __tablename__ = 'bread_order'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date_id = db.Column(db.Integer, db.ForeignKey('bread_order_date.id'))
    type_id = db.Column(db.Integer, db.ForeignKey('bread_type.id'))

    user = db.relationship('User')
    date = db.relationship('BreadOrderDate')
    type = db.relationship('BreadType')

    def __repr__(self):
        return '<BreadOrder by {} on {} for {}>'.format(
            self.user.fullname, self.date.date, self.type.name
        )


class BreadOrderDate(db.Model):

    __tablename__ = 'bread_order_date'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    @property
    def is_editable(self):
        return (self.is_active and
                self.date - datetime.date.today() > datetime.timedelta(days=2))

    def __repr__(self):
        return '<BreadOrderDate {} ({}active)>'.format(
            self.date, "in"*(not self.is_active)
        )


class BreadType(db.Model):

    __tablename__ = 'bread_type'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return '<BreadType {}>'.format(self.name)

    @classmethod
    def from_name(cls, name):
        return cls.query.filter_by(name=name).first()


