#!/usr/bin/env python
# -*- coding: utf-8 -*-
import multiprocessing
import os
import sys
import time
import traceback

from webapp.models.req_error_log import ReqErrorLog

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from webapp import app, db, config_app
from webapp.services import db_service as dbs,data_service as dts

reload(sys)
sys.setdefaultencoding('utf8')
import threading

config_app(app, 'scriptfan.cfg')
ctx = app.app_context()

g_queue = multiprocessing.Queue()

def update_stock(code):
    try:
        ctx.push()
        while not g_queue.empty():
            time.sleep(5)
            item = g_queue.get()
            result = dts.getFinanceData(item)
            dts.updateFinanceData(result)
    except Exception, ex:
        app.logger.warn('stock %s update fail' % code)
        msg = traceback.format_exc()
        eLog = ReqErrorLog("finance_update", code, msg[:1800])
        db.session.add(eLog)
        db.session.commit()


def main():
    ctx.push()
    app.logger.info('stock update begin...')
    # datas = ['000002']
    datas = dbs.get_refresh_finance_stocks()
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

