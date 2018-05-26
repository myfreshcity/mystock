#!/usr/bin/env python
# -*- coding: utf-8 -*-
from celery import Celery

from celery.schedules import crontab

import refresh_stock_holder,refresh_stock_finance,refresh_stock_trade
from refresh_stock_holder import urls_queue, data_queue, ThreadCrawl, ThreadWrite
from webapp import celery, app, config_app
from webapp.services.holder_service import getRefreshStocks

config_app(app, 'scriptfan.cfg')
ctx = app.app_context()

@celery.task
def stock_holder():
    with app.app_context() as ctx:
        refresh_stock_holder.main(ctx)

@celery.task
def stock_finance():
    with app.app_context() as ctx:
        refresh_stock_finance.main(ctx)

@celery.task
def stock_trade():
    with app.app_context() as ctx:
        refresh_stock_trade.main(ctx)


celery.conf.beat_schedule = {
    'refresh_stock_holder': {
        'task': 'mycelery.stock_holder',
        'schedule': crontab(minute='25',hour='1', day_of_week='sat'), #每周六
        # 'schedule': 5.0
    },
    'refresh_stock_finance': {
        'task': 'mycelery.stock_finance',
        'schedule': crontab(minute='25',hour='2', day_of_week='sat'), #每周六
        # 'schedule': 5.0
    },
    'refresh_stock_trade': {
        'task': 'mycelery.stock_trade',
        'schedule': crontab(minute='25',hour='3', day_of_week='sat'), #每周六
        # 'schedule': 5.0
    },
}
