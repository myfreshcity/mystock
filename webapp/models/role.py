from uuid import uuid4
from webapp.services import db

class Role(db.Model):
    """Represents Proected roles."""

    __tablename__ = 'roles'

    id = db.Column(db.String(45), primary_key=True)
    role_name = db.Column(db.String(255), unique=True)
    description = db.Column(db.String(255))

    def __init__(self):
        self.id = str(uuid4())

    def __repr__(self):
        return "<Model Role `{}`>".format(self.role_name)