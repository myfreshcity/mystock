from datetime import datetime

from webapp.services import db


class InvestWarning(db.Model):
    __tablename__ = 'invest_warning'

    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(50))
    content = db.Column(db.String(2000))
    created_time = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, author, content):
        self.author = author
        self.content = content

    def __repr__(self):
        return '<InvestWarning %r>' % self.id

