#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import traceback

from datetime import datetime

from webapp.models.req_error_log import ReqErrorLog

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import threading,multiprocessing
from multiprocessing import Pool
import time
from flask import Flask, render_template, abort, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager, Shell
from webapp import app, db, config_app, register_blueprints, celery
from webapp.services import getHeaders,db_service as ds,data_service as dts,holder_service as hs,ntes_service as ns,xueqiu_service as xues
from webapp.functions import profile


reload(sys)
sys.setdefaultencoding('utf8')
from Queue import Queue

urls_queue = Queue()
data_queue = Queue(maxsize=200)

#共享数据
lock = threading.Lock()

class ThreadCrawl(threading.Thread):

    def __init__(self, ctx, queue, out_queue):
        threading.Thread.__init__(self)
        self.ctx = ctx
        self.queue = queue
        self.out_queue = out_queue

    def run(self):
        while True:
            self.ctx.push()
            item = self.queue.get()
            result = dts.getFinanceData(item)
            if result:
                self.out_queue.put(result)
            self.queue.task_done()


class ThreadWrite(threading.Thread):
    def __init__(self, ctx, queue, lock):
        threading.Thread.__init__(self)
        self.queue = queue
        self.lock = lock
        self.ctx = ctx

    def run(self):
        while True:
            self.ctx.push()
            item = self.queue.get()
            dts.updateFinanceData(item)
            self.queue.task_done()

@profile
def main(ctx):
    #准备数据
    # datas = ['000002']
    datas = ds.get_refresh_finance_stocks()
    
    for d in datas:
        urls_queue.put(d)
    app.logger.info('target stocks size is %s' % urls_queue.qsize())


    for i in range(10):
        t = ThreadCrawl(ctx, urls_queue, data_queue)
        t.setDaemon(True)
        t.start()


    for i in range(10):
        t = ThreadWrite(ctx, data_queue, lock)
        t.setDaemon(True)
        t.start()

    urls_queue.join()
    data_queue.join()
