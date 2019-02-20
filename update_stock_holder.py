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

g_queue = multiprocessing.Queue()

def update_stock(t):
    ctx.push()
    while not g_queue.empty():
        time.sleep(10)
        try:
            item = g_queue.get()
            data = hs.getStockHolderFromNet(item)
            dts.updateStockHolder(data)
        except Exception, ex:
            app.logger.warn('stock %s holder update fail' % item)
            msg = traceback.format_exc()
            eLog = ReqErrorLog("holder_update", item, msg[:1800])
            db.session.add(eLog)
            db.session.commit()
            continue


def main():
    ctx.push()
    app.logger.info('stock holder update begin...')
    # datas = ['000002']
    datas = hs.getRefreshStocks()
    for code in datas:
        g_queue.put(code)

    thread_list = [threading.Thread(target=update_stock, args=(i,)) for i in range(5)]
    for t in thread_list:
        t.start()
    for t in thread_list:
        if t.is_alive():
            t.join()

if __name__ == '__main__':
    main()

