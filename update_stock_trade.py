#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
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

def update_stock(code):
    try:
        ctx.push()
        dts.updateTradeData(code)
    except Exception, ex:
        app.logger.warn('stock %s update fail' % code)
        msg = traceback.format_exc()
        eLog = ReqErrorLog("trade_update", code, msg[:1800])
        db.session.add(eLog)
        db.session.commit()


def update_stocks():
    ctx.push()
    app.logger.info('stock update begin...')
    # datas = ['000002']
    datas = dbs.get_refresh_trade_stocks()
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

