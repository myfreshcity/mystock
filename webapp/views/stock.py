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
from webapp import functions as fn
from flask import current_app as app

blueprint = Blueprint('stock', __name__)


@blueprint.route('/', methods=['GET'])
def index():
    data = ds.getMyStocks('1')
    sdata = []
    for index, row in data.iterrows():
        sdata.append({
            'name':row['name'],
            'code':row.code,
            'price':row.price,
            'mgsy': row.mgsy_ttm,
            'ncode':row['market']+row['code'],
            'sxlv':round(row.price/row.mgjyxjl_ttm,2),
            'sylv':round(row.price/row.mgsy_ttm,2),
            'sjlv': round(row.price/row.mgjzc,2),
            'report_type':row.report_type
        })
    return render_template('stock/index.html', title='备选股', stocks=sdata)


@blueprint.route('/mystock', methods=['GET'])
def mystock():
    data = ds.getMyStocks('0')
    sdata = []
    for index, row in data.iterrows():
        sdata.append({
            'name':row['name'],
            'code':row.code,
            'ncode': row['market'] + row['code'],
            'price':row.price,
            'mgsy': row.mgsy_ttm,
            'sxlv':round(row.price/row.mgjyxjl_ttm,2),
            'sylv':round(row.price/row.mgsy_ttm,2),
            'sjlv': round(row.price/row.mgjzc,2),
            'report_type':row.report_type
        })

    return render_template('stock/mystock.html', title='自选股', stocks=sdata)


@blueprint.route('/<code>', methods=['GET'])
def home(code):
    stock = ds.getStock(code)
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
    yysr = [] #营业收入
    jlr = [] #净利润
    jyjxjl = [] #经营性净现金流
    gdqy = [] #股东权益


    code = request.form['code'][2:]
    category = request.form['category']

    if category=='year':
        df = ds.get_year_stock_revenue(code)
        for index, row in df.iterrows():
            yysr.append(fn.get_data_array(row['report_type'], row['yysr']))
            jlr.append(fn.get_data_array(row['report_type'], row['kjlr']))
            jyjxjl.append(fn.get_data_array(row['report_type'], row['jyjxjl']))
            gdqy.append(fn.get_data_array(row['report_type'], row['gdqy']))
    else:
        yysr_1=[];jlr_1=[];jyjxjl_1=[];gdqy_1=[]
        yysr_2=[];jlr_2=[];jyjxjl_2=[];gdqy_2=[]
        yysr_3=[];jlr_3=[];jyjxjl_3=[];gdqy_3=[]

        (df1,df2,df3) = ds.get_quart_stock_revenue(code)

        for index, row in df1.iterrows():
            yysr_1.append(fn.get_data_array(row['report_type'], row['yysr']))
            jlr_1.append(fn.get_data_array(row['report_type'], row['kjlr']))
            jyjxjl_1.append(fn.get_data_array(row['report_type'], row['jyjxjl']))
            gdqy_1.append(fn.get_data_array(row['report_type'], row['gdqy']))

        for index, row in df2.iterrows():
            yysr_2.append(fn.get_data_array(row['report_type'], row['yysr']))
            jlr_2.append(fn.get_data_array(row['report_type'], row['kjlr']))
            jyjxjl_2.append(fn.get_data_array(row['report_type'], row['jyjxjl']))
            gdqy_2.append(fn.get_data_array(row['report_type'], row['gdqy']))

        for index, row in df3.iterrows():
            yysr_3.append(fn.get_data_array(row['report_type'], row['yysr']))
            jlr_3.append(fn.get_data_array(row['report_type'], row['kjlr']))
            jyjxjl_3.append(fn.get_data_array(row['report_type'], row['jyjxjl']))
            gdqy_3.append(fn.get_data_array(row['report_type'], row['gdqy']))


        yysr = [yysr_1,yysr_2,yysr_3]
        jlr = [jlr_1, jlr_2, jlr_3]
        jyjxjl = [yysr_1, yysr_2, yysr_3]
        gdqy = [yysr_1, yysr_2, yysr_3]

    return jsonify(cat=category,data={'yysr':yysr,'jlr':jlr,'jyjxjl':jyjxjl,'drate':gdqy})


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