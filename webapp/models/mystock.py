from webapp.services import db
from datetime import datetime

class MyStock(db.Model):
    __tablename__ = 'my_stocks'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(255))
    name = db.Column(db.String(255))
    market = db.Column(db.String(255))
    tag = db.Column(db.String(255))
    flag = db.Column(db.Integer,default=1)
    in_price = db.Column(db.Numeric,default=0)
    in_date = db.Column(db.Date)
    created_time = db.Column(db.DateTime, default=datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, code, name, market):
        self.code = code
        self.name = name
        self.market = market
        self.tag = ''

    def __repr__(self):
        return '<Stock %r>' % self.name

    @property
    def ncode(self):
      return self.market+self.code

    @classmethod
    def get_by_code(code):
        return MyStock.query.filter_by(code=code).first()