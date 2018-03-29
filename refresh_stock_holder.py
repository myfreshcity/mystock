#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import threading,multiprocessing
from multiprocessing import Pool
import time
from flask import Flask, render_template, abort, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager, Shell
from webapp import app, db, config_app,register_blueprints
from webapp.services import db_service as ds,data_service as dts,holder_service as hs
from webapp.functions import profile


reload(sys)
sys.setdefaultencoding('utf8')
from Queue import Queue

urls_queue = Queue()
data_queue = Queue(maxsize=200)

#共享数据
lock = threading.Lock()
config_app(app, 'scriptfan.cfg')
ctx = app.app_context()

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
            data = hs.getStockHolderFromNet(item)
            self.out_queue.put(data)
            self.queue.task_done()


class ThreadWrite(threading.Thread):

    def __init__(self, queue, lock,ctx):
        threading.Thread.__init__(self)
        self.queue = queue
        self.lock = lock
        self.ctx = ctx

    def run(self):
        while True:
            item = self.queue.get()
            self._parse_data(item)
            self.queue.task_done()

    def _parse_data(self, item):
        self.ctx.push()
        dts.updateStockHolder(item)
        #print 'write %s' % item

@profile
def main():
    ctx.push()
    #准备数据
    datas = hs.getRefreshStocks()
    for d in datas:
        urls_queue.put(d)
    app.logger.info('target stocks size is %s' % urls_queue.qsize())

    #开线程读取数据
    for i in range(10):
        t = ThreadCrawl(ctx, urls_queue, data_queue)
        t.setDaemon(True)
        t.start()

    #开线程消费数据
    for i in range(10):
        t = ThreadWrite(data_queue,lock,ctx)
        t.setDaemon(True)
        t.start()

    urls_queue.join()
    data_queue.join()

if __name__ == '__main__':
    main()
