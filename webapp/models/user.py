from uuid import uuid4

from datetime import datetime
from flask import current_app
from flask_login import AnonymousUserMixin
from itsdangerous import SignatureExpired, BadSignature, Serializer

from webapp.extensions import cache, bcrypt
from webapp.models.role import Role
from webapp.services import users_roles, db


class User(db.Model):
    """Represents Proected users."""

    # Set the name for table
    __tablename__ = 'users'

    id = db.Column(db.String(45), primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(255))
    last_login_time = db.Column(db.DateTime, default=datetime.now)

    # many to many: user <==> roles
    roles = db.relationship(
        'Role',
        secondary=users_roles,
        backref=db.backref('users', lazy='dynamic'))

    def __init__(self, username, password):
        self.id = str(uuid4())
        self.username = username
        self.password = self.set_password(password)

        # Setup the default-role for user.
        default = Role.query.filter_by(name="default").one()
        self.roles.append(default)

    def __repr__(self):
        """Define the string format for instance of User."""
        return "<Model User `{}`>".format(self.id)

    def set_password(self, password):
        """Convert the password to cryptograph via flask-bcrypt"""
        return bcrypt.generate_password_hash(password)

    def check_password(self, password):
        """Check the entry-password whether as same as user.password."""
        return bcrypt.check_password_hash(self.password, password)

    def is_authenticated(self):
        """Check the user whether logged in."""

        # Check the User's instance whether Class AnonymousUserMixin's instance.
        if isinstance(self, AnonymousUserMixin):
            return False
        else:
            return True

    def is_active():
        """Check the user whether pass the activation process."""

        return True

    def is_anonymous(self):
        """Check the user's login status whether is anonymous."""

        if isinstance(self, AnonymousUserMixin):
            return True
        else:
            return False

    def get_id(self):
        """Get the user's uuid from database."""

        return unicode(self.id)

    @staticmethod
    @cache.memoize(60)
    def verify_auth_token(token):
        """Validate the token whether is night."""

        serializer = Serializer(
            current_app.config['SECRET_KEY'])
        try:
            # serializer object already has tokens in itself and wait for
            # compare with token from HTTP Request /api/posts Method `POST`.
            data = serializer.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None

        user = User.query.filter_by(id=data['id']).first()
        return user