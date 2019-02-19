#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import traceback

from webapp.models import Stock
from webapp.models.req_error_log import ReqErrorLog

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import threading,multiprocessing
from multiprocessing import Pool
import time
from flask import Flask, render_template, abort, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager, Shell
from webapp import app, db, config_app, register_blueprints, celery
from webapp.services import db_service as ds,data_service as dts,holder_service as hs
from webapp.functions import profile


reload(sys)
sys.setdefaultencoding('utf8')
from Queue import Queue
import threading
import time


config_app(app, 'scriptfan.cfg')
ctx = app.app_context()

def update_stock(code):
    try:
        ctx.push()
        app.logger.info('%s' % code)
        data = hs.getStockHolderFromNet(code)
        dts.updateStockHolder(data)
    except Exception, ex:
        app.logger.warn('stock %s holder update fail' % code)
        msg = traceback.format_exc()
        eLog = ReqErrorLog("holder_update", code, msg[:1800])
        db.session.add(eLog)
        db.session.commit()


def update_stocks():
    ctx.push()
    app.logger.info('stock holder update begin...')
    # datas = ['000002']
    datas = hs.getRefreshStocks()
    datas = datas[:10]
    thread_list = [threading.Thread(target=update_stock, args=(i,)) for i in datas]
    for t in thread_list:
        t.start()
    for t in thread_list:
        if t.is_alive():
            t.join()

def main():
    update_stocks()
    threading.Timer(20, main).start()


if __name__ == '__main__':
    main()

