from webapp.services import db
from datetime import datetime
import urllib2,re

class Stock(db.Model):
    __tablename__ = 'stocks'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(255))
    name = db.Column(db.String(255))

    def __init__(self, name, code):
        self.name = name
        self.code = code

    def __repr__(self):
        return '<Stock %r>' % self.name

    @classmethod
    def find_by_code(self,cd):
        return Stock.query.filter_by(code=cd).first()

    @property
    def current_price(self):
        data = self.query_trade_data()
        return round(float(data[3]), 2)

    def query_trade_data(self):
        url = "http://hq.sinajs.cn/list=" + self.code
        req = urllib2.Request(url)
        res_data = urllib2.urlopen(req).read()
        match = re.search(r'".*"', res_data).group(0)
        trade_data = match.split(',')
        return trade_data
