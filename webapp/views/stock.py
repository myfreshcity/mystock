#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, Response, request, session, g, redirect, url_for, abort, \
    render_template, flash
from flask import json, jsonify, Blueprint, render_template
import pandas as pd
import time
import urllib
from webapp.services import db_service as ds,data_service as dts
from webapp.models import MyStock
from webapp import functions as fn
from flask import current_app as app

blueprint = Blueprint('stock', __name__)


@blueprint.route('/', methods=['GET'])
def index():
    data = dts.getMyStocks('1')
    sdata = []
    for index, row in data.iterrows():
        sdata.append({
            'id':row['id'],
            'name':row['name'],
            'code':row.code,
            'price':row.price,
            'grow_type': row.grow_type,
            'mvalue': round((row.price*row['zgb'])/(10000*10000),2),
            'mgsy': row.mgsy_ttm,
            'ncode':row['market']+row['code'],
            'sxlv':round(row.price/row.mgjyxjl_ttm,2),
            'sylv':round(row.price/row.mgsy_ttm,2),
            'sjlv': round(row.price/row.mgjzc,2),
            'launch_date': row['launch_date'],
            'report_type':row.report_type
        })
    return render_template('stock/stock_list.html', title='备选股', stocks=sdata)


@blueprint.route('/mystock', methods=['GET'])
def mystock():
    data = dts.getMyStocks('0')
    sdata = []
    for index, row in data.iterrows():
        sdata.append({
            'name':row['name'],
            'code':row.code,
            'grow_type': row.grow_type,
            'ncode': row['market'] + row['code'],
            'price':row.price,
            'in_price': row['in_price'],
            'in_date': row['in_date'],
            'mprice': row['mprice'],
            'p1': 0 if row.in_price==0 else round((row.price-row.in_price)*100/row.in_price, 2),
            'p2': 0 if row.mprice==0 else round((row.price-row.mprice)*100/row.mprice, 2),
            'mvalue': round((row.price * row['zgb']) / (10000 * 10000), 2),
            'mgsy': row.mgsy_ttm,
            'sxlv':round(row.price/row.mgjyxjl_ttm,2),
            'sylv':round(row.price/row.mgsy_ttm,2),
            'sjlv': round(row.price/row.mgjzc,2),
            'report_type':row.report_type
        })

    return render_template('stock/mystock_list.html', title='自选股', stocks=sdata)


@blueprint.route('/<code>', methods=['GET'])
def home(code):
    stock = ds.getStock(code[2:])
    price = stock.current_price
    #app.logger.info('stock current price is:'+stock.current_price)
    dateTime = pd.date_range(start='20001231', periods=15, freq='3M').to_series()
    date = [pd.to_datetime(str(value)).strftime('%Y-%m-%d') for value in dateTime]
    return render_template('stock/home.html', title=stock.name, mydate=date,code=code,price=price)

@blueprint.route('/blog/<code>', methods=['GET'])
def blog(code):
    stock = ds.getMyStock(code)
    #price = stock.current_price
    return render_template('stock/blog.html', title=stock.name, code=code)

@blueprint.route('/valuation/<code>', methods=['GET'])
def valuation(code):
    stock = ds.getMyStock(code)
    #price = stock.current_price
    return render_template('stock/valuation.html', title=stock.name, code=code)

@blueprint.route('/valuationJson', methods=['POST'])
def valuationJson():
    code = request.form['code']
    period = int(request.form['period'])
    df = ds.getStockValuationN(code[2:],period)

    close = []
    pe = []
    ps = []
    pcf = []
    pb = []
    tableData = []

    for index, row in df.iterrows():
        tcp = row['t_cap']
        rclose = row['close']
        spe = 0 if row['jlr_ttm']== 0 else round(tcp/row['jlr_ttm'],2)
        sps = 0 if row['zyysr_ttm']== 0 else round(tcp/row['zyysr_ttm'],2)
        spcf = 0 if row['jyjxjl_ttm']== 0 else round(tcp/row['jyjxjl_ttm'],2)
        spb = 0 if row['gdqy'] == 0 else round(tcp / row['gdqy'], 2)
        tdate = row['trade_date'].strftime('%Y-%m-%d')

        close.append([tdate,rclose])
        pe.append([tdate,spe])
        ps.append([tdate, sps])
        pcf.append([tdate, spcf])
        pb.append([tdate, spb])

        tableData.append(
            [tdate,
             rclose,
             spe,
             sps,
             spcf,
             spb,
             tcp,
             row['gdqy'],
             row['jlr'],
             row['jlr_ttm'],
             row['zyysr'],
             row['zyysr_ttm'],
             row['jyjxjl'],
             row['jyjxjl_ttm']
             ]
        )

    return jsonify(data={'close': close, 'pe': pe, 'ps': ps, 'pcf': pcf,'pb':pb,'tableData':tableData},period=period)


@blueprint.route('/revenueJson', methods=['POST'])
def revenueJson():
    yysr = [] #营业收入
    jlr = [] #净利润
    jyjxjl = [] #经营性净现金流
    roe = [] #净资产收益率

    code = request.form['code'][2:]
    quarter = int(request.form['quarter'])
    df = ds.get_quarter_stock_revenue(code, quarter)

    for index, row in df.iterrows():
        yysr.append(fn.get_data_array(row['report_type'], row['yysr']))
        jlr.append(fn.get_data_array(row['report_type'], row['kjlr']))
        jyjxjl.append(fn.get_data_array(row['report_type'], row['jyjxjl']))
        roe.append([row['report_type'].encode('utf-8'), round(row['roe'], 2)])

    return jsonify(data={'yysr':yysr,'jlr':jlr,'jyjxjl':jyjxjl,'roe':roe},tableData=json.loads(df.to_json(orient="records")))


@blueprint.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        code = request.form['code']
        app.logger.debug('code:' + code)
        msg = ds.addMystock(code)
        if msg:
            flash(msg)
        return redirect('stock')
    else:
        return render_template('stock/add.html')

@blueprint.route('/get_basic', methods=['GET'])
def get_basic():
    code = request.args.get('code')
    st = ds.getStock(code[2:])
    return jsonify(msg='true',stock={
        'desc':st.desc,
        'grow_type':st.grow_type
        })

@blueprint.route('/update_basic', methods=['POST'])
def update_basic():
    code = request.form['code']
    desc = request.form['desc']
    grow_type = request.form['growType']
    ds.updateStock(code[2:],desc,grow_type)
    return jsonify(msg='true')

@blueprint.route('/saveInPrice', methods=['POST'])
def saveInPrice():
    code = request.form['code']
    price = request.form['price']
    in_date = request.form['date']
    ds.updateStockInPrice(code,price,in_date)
    return jsonify(msg='true')

@blueprint.route('/remove', methods=['POST'])
def remove():
    code = request.form['code']
    ds.removeMystock(code)
    return jsonify(msg='true')

@blueprint.route('/rollback', methods=['POST'])
def rollback():
    code = request.form['code']
    ds.rollbackStock(code)
    return jsonify(msg='true')

@blueprint.route('/del', methods=['POST'])
def hardRemove():
    code = request.form['code']
    ds.hardRemoveMystock(code)
    return jsonify(msg='true')

@blueprint.route('/queryComments', methods=['GET', 'POST'])
def queryComments():
    code = request.form['code']
    df = ds.queryComment(code)
    data = []
    for x in df:
        data.append({
            'id' : x.id,
            'date':x.created_time.strftime('%Y-%m-%d'),
            'content':x.content
        })
    return jsonify(data=data)


@blueprint.route('/addComment', methods=['GET', 'POST'])
def addComment():
    code = request.form['code']
    content = request.form['content']
    app.logger.debug('code:' + code)
    try:
        c = ds.addComment(code,content)
        return jsonify(msg='true',
                       data={'date':c.created_time.strftime('%Y-%m-%d'),'content':c.content,'id':c.id}
                       )
    except:
        return jsonify(msg='false')

@blueprint.route('/updateComment', methods=['GET', 'POST'])
def updateComment():
    cid = request.form['cid']
    content = request.form['content']
    try:
        c = ds.updateComment(cid, content)
        return jsonify(msg='true',
                       data={'id': cid, 'content': c.content}
                       )
    except:
        return jsonify(msg='false')