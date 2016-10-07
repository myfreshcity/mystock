from webapp.services import db
from datetime import datetime

class RelationStock(db.Model):
    __tablename__ = 'relation_stocks'

    id = db.Column(db.Integer, primary_key=True)
    main_stock = db.Column(db.String(255))
    relation_stock = db.Column(db.String(255))
    created_time = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, mcode, scode):
        self.main_stock = mcode
        self.relation_stock = scode

    def __repr__(self):
        return '<RelationStock %r>' % self.main_stock

