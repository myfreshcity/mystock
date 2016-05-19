from webapp.services import db
from datetime import datetime

class FinanceBasic(db.Model):
    __tablename__ = 'stock_finance_basic'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(255))
    report_type = db.Column(db.String(255))
    mgsy = db.Column(db.Numeric)
    mgjzc = db.Column(db.Numeric)
    mgjyxjl = db.Column(db.Numeric)

    yysr = db.Column(db.Numeric)
    kjlr = db.Column(db.Numeric)
    jyjxjl = db.Column(db.Numeric)


    def __init__(self):
        pass

    def __repr__(self):
        return '<FinanceBasic %r>' % self.name
