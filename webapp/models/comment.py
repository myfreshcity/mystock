from uuid import uuid4

from webapp.services import db
from datetime import datetime
import urllib2,re

class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.String(45), primary_key=True)
    stock = db.Column(db.String(255))
    user_id = db.Column(db.String(45))
    ct_flag = db.Column(db.String(10), default="-1")
    content = db.Column(db.String(255))

    parent_id = db.Column(db.String(45))

    created_time = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, stock, content):
        self.id = str(uuid4())
        self.stock = stock
        self.content = content

    def __repr__(self):
        return '<Comment %r>' % self.id

