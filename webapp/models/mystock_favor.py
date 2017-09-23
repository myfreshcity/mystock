from webapp.services import db
from datetime import datetime

class MyStockFavor(db.Model):
    __tablename__ = 'my_stock_favor'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(255))
    title = db.Column(db.String(255))
    url = db.Column(db.String(255))
    src_type = db.Column(db.String(50))
    pub_date = db.Column(db.Date)
    user_id = db.Column(db.String(45))
    created_time = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, code, title, url,pub_date,src_type):
        self.code = code
        self.title = title
        self.url = url
        self.pub_date = pub_date
        self.src_type = src_type

    def __repr__(self):
        return '<MyStockFavor %r>' % self.id

