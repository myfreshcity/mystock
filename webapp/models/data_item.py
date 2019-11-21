# -*- coding: utf-8 -*-

from webapp.services import db


class DataItem(db.Model):
    __tablename__ = 'data_item'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    update_time = db.Column(db.DateTime)

    def __init__(self, name, update_time):
        self.name = name
        self.update_time = update_time

    def __repr__(self):
        return '<User %r>' % self.name

