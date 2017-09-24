#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import (Blueprint, render_template, redirect,
                   flash, url_for, request)
from flask import json,jsonify,render_template

import pandas as pd
import time
from datetime import datetime
from webapp.models import MyStock,Stock,DataItem,Comment
from webapp.services import getHeaders,getXueqiuHeaders, data_service as dts,db_service as dbs,db,holder_service as hs,ntes_service as ns,xueqiu_service as xues
from flask import current_app as app

blueprint = Blueprint('setting', __name__)

@blueprint.route('/', methods = ['GET'])
def index():
    data = dbs.getItemDates()
    return render_template('/setting/index.html', title='设置',dataItems=data)

@blueprint.route('/update/', methods = ['GET','POST'])
def update():
    code = request.form['code'][2:]
    # 更新财务数据
    flag = ns.updateFinanceData(code)
    headers = getHeaders("http://xueqiu.com")
    xues.updateAssetWebData(code,headers)
    xues.updateIncomeWebData(code,headers)
    xues.updateCashWebData(code,headers)
    # 更新交易数据
    ns.updateTradeData(code)

    dbs.get_global_trade_data()
    dbs.get_global_finance_data()
    dbs.get_global_basic_data()

    return jsonify(msg=flag)

@blueprint.route('/updateHolder/', methods = ['GET','POST'])
def updateHolder():
    code = request.args.get('code')
    #heads = getHeaders('https://xueqiu.com')
    (session,heads) = getXueqiuHeaders()
    hs.updateStockHolder(code,session,heads)
    return jsonify(msg=True)

@blueprint.route('/updateAll/<int:cat>', methods = ['GET','POST'])
def updateAll(cat):
    #获得所有股票代码列表
    stocks = db.session.query(MyStock).filter(MyStock.code != '000001').all()
    if cat == 1:
        for st in stocks:
            app.logger.info('checking finance data for:' + st.code)
            dts.updateFinanceBasic(st.code)
        item = db.session.query(DataItem).filter_by(id=1).first()
        item.update_time = datetime.now()
        db.session.save(item)
    elif cat == 2:
        for st in stocks:
            app.logger.info('checking trade data for:' + st.code)
            dts.updateTradeBasic(st.code,st.market)
        item = db.session.query(DataItem).filter_by(id=2).first()
        item.update_time = datetime.now()
        db.session.save(item)

    return render_template('/setting/index.html')
