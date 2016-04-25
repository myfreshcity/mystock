#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, Response, request, session, g, redirect, url_for, abort, \
    render_template, flash
from flask import json, jsonify, Blueprint, render_template
import pandas as pd
import time
import urllib
from webapp.services import db_service as ds
from webapp.models import MyStock
from flask import current_app as app

blueprint = Blueprint('stock', __name__)


@blueprint.route('/', methods=['GET'])
def index():
    return render_template('stock/index.html', title='股票')


@blueprint.route('/mystock', methods=['GET'])
def mystock():
    data = ds.getMyStocks()
    return render_template('stock/mystock.html', title='自选股', stocks=data)


@blueprint.route('/valuation/<code>', methods=['GET'])
def valuation(code):
    stock = ds.getStock(code)
    price = stock.current_price
    #app.logger.info('stock current price is:'+stock.current_price)
    dateTime = pd.date_range(start='20001231', periods=15, freq='3M').to_series()
    date = [pd.to_datetime(str(value)).strftime('%Y-%m-%d') for value in dateTime]
    return render_template('stock/valuation.html', title=stock.name, mydate=date,code=code,price=price)


@blueprint.route('/valuationJson', methods=['POST'])
def valuationJson():
    code = request.form['code']
    category = request.form['category']
    price = request.form['price']
    df = ds.getStockValuation(code,category)

    close = [[date.encode('utf-8'), round(val, 2)] for date, val in zip(df.index, df['close'])]

    pe = [[date.encode('utf-8'), round(val, 2)] for date, val in zip(df.index, df['pe'])]
    ps = [[date.encode('utf-8'), round(val, 2)] for date, val in zip(df.index, df['ps'])]
    pcf = [[date.encode('utf-8'), round(val, 2)] for date, val in zip(df.index, df['pcf'])]

    tableData = []
    for index, row in df.iterrows():
        tableData.append(
            [index.encode('utf-8'),
             row['close'],
             round(row['pe'],2),
             round(row['ps'],2),
             round(row['pcf'],2),
             round(row['mgsy_ttm'],2),
             round(row['mgyysr_ttm'],2),
             round(row['mgjyxjl_ttm'],2)
             ]
        )

    return jsonify(data={'close': close, 'pe': pe, 'ps': ps, 'pcf': pcf,'tableData':tableData})


@blueprint.route('/revenueJson', methods=['POST'])
def revenueJson():
    code = request.form['code']
    df = ds.getStockRevenue(code)
    yysr = [[date.encode('utf-8'), round(val / 1000000, 2)] for date, val in zip(df.index, df['yysr'])]
    jlr = [[date.encode('utf-8'), round(val / 1000000, 2)] for date, val in zip(df.index, df['jlr'])]
    jyjxjl = [[date.encode('utf-8'), round(val / 1000000, 2)] for date, val in zip(df.index, df['jyjxjl'])]
    drate = [[date.encode('utf-8'), round(val, 2)] for date, val in zip(df.index, df['drate'])]
    dateTime = pd.date_range(start='20001231', periods=15, freq='12M').to_series()
    date = [pd.to_datetime(str(value)).strftime('%Y-%m-%d') for value in dateTime]
    return jsonify(data={'yysr':yysr,'jlr':jlr,'jyjxjl':jyjxjl,'drate':drate})


@blueprint.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        code = request.form['code']
        app.logger.debug('code:' + code)
        ds.addMystock(code)
        return redirect('stock/mystock')
    else:
        return render_template('stock/add.html')


@blueprint.route('/remove', methods=['POST'])
def remove():
    code = request.form['code']
    ds.removeMystock(code)
    return jsonify(msg='true')
