from datetime import datetime

from webapp.services import db


class ReqErrorLog(db.Model):
    __tablename__ = 'req_error_log'

    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(50))
    key = db.Column(db.String(255))
    msg = db.Column(db.String(2000))
    created_time = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, action, key, msg):
        self.action = action
        self.key = key
        self.msg = msg

    def __repr__(self):
        return '<ReqErrorLog %r>' % self.id

