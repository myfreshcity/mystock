from webapp.services import db
from datetime import datetime

class MyHolderFavor(db.Model):
    __tablename__ = 'my_holder_favor'

    id = db.Column(db.Integer, primary_key=True)
    holder_code = db.Column(db.String(255))
    holder_name = db.Column(db.String(255))
    amt = db.Column(db.Integer, default=1)
    user_id = db.Column(db.String(45))
    created_time = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, code, name, uid):
        self.holder_code = code
        self.holder_name = name
        self.user_id = uid

    def __repr__(self):
        return '<MyHolderFavor %r>' % self.id

