#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, Response, request, session, g, redirect, url_for, abort, \
    render_template, flash
from flask import json, jsonify, Blueprint, render_template
import pandas as pd
import time
import urllib
from webapp.services import db_service as ds,data_service as dts,holder_service as hs
from webapp.models import MyStock
from webapp import functions as fn
from flask import current_app as app

blueprint = Blueprint('detail', __name__)

@blueprint.route('/peJson', methods=['GET'])
def peJson():
    code = request.args.get('code')[2:]
    period = 5 #最近5年
    quarter = 4 #第4季度

    valuationArray = []
    valuationDf = ds.getStockValuationN(code,period)
    for index, row in valuationDf.iterrows():
        tcp = row['t_cap']
        spe = 0 if row['jlr_ttm']== 0 else round(tcp/row['jlr_ttm'],2)
        tdate = row['trade_date'].strftime('%Y-%m-%d')
        valuationArray.append([tdate,spe])

    actualArray = []
    actualRateArray = []
    tableData = []

    valueDf = ds.get_quarter_stock_revenue(code)
    for index, row in valueDf.iterrows():
        jlr_grow_rate = round(row['jlr_grow_rate'] * 100, 2)
        report_type = row['report_type'].strftime('%Y-%m-%d')
        actualArray.append([report_type, row['jlr']])
        actualRateArray.append([report_type,jlr_grow_rate])

        tableData.append(
            [report_type,
             format(row['zyysr'], ','),
             format(row['jlr'], ','),
             format(row['jyjxjl'], ','),
             round(row['zyysr_grow_rate']*100,2),
             round(row['jlr_grow_rate'] * 100, 2),
             round(row['jyjxjl_grow_rate'] * 100, 2)
             ]
        )
    return jsonify(data={'actualRate':actualRateArray,'actual': actualArray, 'valuation': valuationArray, 'tableData':tableData},period=period)

@blueprint.route('/debetJson', methods=['GET'])
def debetJson():
    code = request.args.get('code')

    fzlArray = []
    dqfzArray = []
    ldbArray = []
    tableData = []

    valueDf = ds.get_revenue_df(code).head(20)
    for index, row in valueDf.iterrows():
        report_type = row['report_type'].strftime('%Y-%m-%d')
        fzl = round(row.zfz * 100.0 / row.zzc, 2) #负债率
        dqfz = round(row.ldfz * 100.0 / row.zzc, 2) #短期负债率
        ldb = round(row.ldzc / row.ldfz, 2)  # 流动比

        fzlArray.append([report_type, fzl])
        dqfzArray.append([report_type,dqfz])
        ldbArray.append([report_type, ldb])

        tableData.append(
            [report_type,
             round(row['zzc']/10000, 2),
             round(row['zfz']/10000, 2),
             #format(row['ldzc'], ','),
             #format(row['ldfz'], ','),
             round(row['gdqy']/10000, 2),
             round(row['ch']/10000, 2),
             round(row['yszk']/10000, 2),
             fzl,
             dqfz,
             ldb
             ]
        )

    return jsonify(data={'fzl':fzlArray,'dqfz': dqfzArray,'ldb': ldbArray, 'tableData':tableData})


@blueprint.route('/debetExJson', methods=['GET'])
def debetExJson():
    code = request.args.get('code')
    quarter = int(request.args.get('quarter'))

    chArray = []
    chRateArray = []
    yszkArray = []
    yszkRateArray = []
    zyysrArray = []

    valueDf = ds.get_quarter_stock_revenue(code,quarter)
    for index, row in valueDf.iterrows():
        report_type = row['report_type'].strftime('%Y-%m-%d')

        chRate = round(row.ch * 100.0 / row.zyysr_ttm, 2)  # 存货比
        yszkRate = round(row.yszk * 100.0 / row.zyysr_ttm, 2)  # 应收帐款比

        chRateArray.append([report_type, chRate])
        yszkRateArray.append([report_type, yszkRate])

        chArray.append([report_type, row.ch])
        yszkArray.append([report_type, row.yszk])
        zyysrArray.append([report_type, row.zyysr_ttm])


    return jsonify(data={'zyysr':zyysrArray,'ch': chArray,'yszk': yszkArray,'chb': chRateArray,'yszkb': yszkRateArray})


@blueprint.route('/pcfJson', methods=['GET'])
def pcfJson():
    code = request.args.get('code')
    period = 5 #最近5年


    valuationArray = []
    valuationDf = ds.getStockValuationN(code,period)
    for index, row in valuationDf.iterrows():
        tcp = row['t_cap']
        spe = 0 if row['jyjxjl_ttm']== 0 else round(tcp/row['jyjxjl_ttm'],2)
        tdate = row['trade_date'].strftime('%Y-%m-%d')
        valuationArray.append([tdate,spe])

    actualArray = []
    actualRateArray = []
    tableData = []

    valueDf = ds.get_quarter_stock_revenue(code)
    for index, row in valueDf.iterrows():
        jlr_grow_rate = round(row['jyjxjl_grow_rate'] * 100, 2)
        report_type = row['report_type'].strftime('%Y-%m-%d')
        actualArray.append([report_type, row['jyjxjl']])
        actualRateArray.append([report_type,jlr_grow_rate])

        tableData.append(
            [report_type,
             format(row['zyysr'], ','),
             format(row['jlr'], ','),
             format(row['jyjxjl'], ','),
             round(row['zyysr_grow_rate']*100,2),
             round(row['jlr_grow_rate'] * 100, 2),
             round(row['jyjxjl_grow_rate'] * 100, 2)
             ]
        )
    return jsonify(data={'actualRate':actualRateArray,'actual': actualArray, 'valuation': valuationArray, 'tableData':tableData},period=period)

@blueprint.route('/psJson', methods=['GET'])
def psJson():
    code = request.args.get('code')
    period = 5 #最近5年

    valuationArray = []
    valuationDf = ds.getStockValuationN(code,period)
    for index, row in valuationDf.iterrows():
        tcp = row['t_cap']
        spe = 0 if row['zyysr_ttm']== 0 else round(tcp/row['zyysr_ttm'],2)
        tdate = row['trade_date'].strftime('%Y-%m-%d')
        valuationArray.append([tdate,spe])

    actualArray = []
    actualRateArray = []
    tableData = []

    valueDf = ds.get_quarter_stock_revenue(code)
    for index, row in valueDf.iterrows():
        jlr_grow_rate = round(row['zyysr_grow_rate'] * 100, 2)
        report_type = row['report_type'].strftime('%Y-%m-%d')
        actualArray.append([report_type, row['zyysr']])
        actualRateArray.append([report_type,jlr_grow_rate])

        tableData.append(
            [report_type,
             format(row['zyysr'], ','),
             format(row['jlr'], ','),
             format(row['jyjxjl'], ','),
             round(row['zyysr_grow_rate']*100,2),
             round(row['jlr_grow_rate'] * 100, 2),
             round(row['jyjxjl_grow_rate'] * 100, 2)
             ]
        )
    return jsonify(data={'actualRate':actualRateArray,'actual': actualArray, 'valuation': valuationArray, 'tableData':tableData},period=period)

@blueprint.route('/holderJson', methods=['GET'])
def holderJson():
    code = request.args.get('code')
    reportDate = request.args.get('report_date')
    direction = request.args.get('forward_dirc')


    tableData = []
    (_report_date,_result_df) = hs.getStockHolder(code,reportDate,direction)
    for index, row in _result_df.iterrows():
        report_date = row['report_date'].strftime('%Y-%m-%d')
        tableData.append(
            [report_date,
             row['name'],
             row['code'],
             row['rate'],
             format(row['amount'], ','),
             row['var']
             ])

    sizeArray = []
    sumArray = []
    (size_df,sum_df) = hs.getStockHolderHistory(code)
    it_1 = size_df.iterrows()
    it_2 = sum_df.iterrows()
    for index, row in it_1:
        sizeArray.append([index.strftime('%Y-%m-%d'), row['size']])
    for index, row in it_2:
        sumArray.append([index.strftime('%Y-%m-%d'), row['sum']])

    return jsonify(data={'holderSize':sizeArray,'holderSum': sumArray, 'tableData':tableData,'reportDate':_report_date})

@blueprint.route('/holderTrackJson', methods=['GET'])
def holderTrackJson():
    holder_code = request.args.get('hcode')

    tableData = []
    df = hs.getStockHolderTrack(holder_code)
    for index, row in df.iterrows():
        report_date = row['report_date'].strftime('%Y-%m-%d')
        tableData.append(
            [report_date,
             row['code'],
             row['name'],
             row['rate'],
             format(row['amount'], ',')
             ])

    return jsonify(data={'tableData':tableData})


@blueprint.route('/relationJson', methods=['GET'])
def relationJson():
    code = request.args.get('code')
    tableData = []
    try:
        df = dts.getRelationStock(code)
        for index, row in df.iterrows():
            tableData.append(
                [row['code'],
                 row['name'],
                 row['pe_ttm'],
                 row['eve_ttm'],
                 row['pcf_ttm'],
                 row['ps_ttm'],
                 row['pb_ttm'],
                 row['peg']
                 ])
    except Exception, ex:
        app.logger.error(code+':',ex)
    return jsonify(data={'tableData':tableData})

@blueprint.route('/growJson', methods=['GET'])
def growJson():
    code = request.args.get('code')[2:]
    actualArray = []
    actualRateArray = []

    valueDf = ds.get_revenue_df(code)
    valueDf = valueDf.head(5*4)
    for index, row in valueDf.iterrows():
        jlr_grow_rate = round(row['jlr_rate'] * 100, 2)
        report_type = row['report_type'].strftime('%Y-%m-%d')
        actualArray.append([report_type, row['jlr_ttm']])
        actualRateArray.append([report_type,jlr_grow_rate])

    return jsonify(data={'actualRate':actualRateArray,'actual': actualArray})

@blueprint.route('/cashRateJson', methods=['GET'])
def cashRateJson():
    code = request.args.get('code')[2:]
    actualArray = []
    actualRateArray = []

    valueDf = ds.get_cash_rate(code)
    valueDf = valueDf.head(5*4)
    for index, row in valueDf.iterrows():
        jlr_grow_rate = round(row['cash_rate_var'] * 100, 2)
        report_type = index.strftime('%Y-%m-%d')
        actualArray.append([report_type, row['cash_rate']])
        actualRateArray.append([report_type,jlr_grow_rate])

    return jsonify(data={'cashRate':actualRateArray,'cash': actualArray})

@blueprint.route('/163News', methods=['GET'])
def get163News():
    code = request.args.get('code')[2:]
    index = request.args.get('index')
    tableData = dts.get163News(code,index)
    return jsonify(data={'tableData':tableData})

@blueprint.route('/QQNews', methods=['GET'])
def getQQNews():
    code = request.args.get('code')
    index = request.args.get('index')
    tableData = dts.getQQNews(code,index)
    return jsonify(data={'tableData':tableData})

@blueprint.route('/linkContent', methods=['GET'])
def getLinkContent():
    url = request.args.get('url')
    src = request.args.get('src')
    content = dts.getLinkContent(url,src)
    return content

@blueprint.route('/addFavoriate', methods=['GET', 'POST'])
def addFavoriate():
    code = request.form['code']
    title = request.form['title']
    url = request.form['url']
    dateTime = request.form['dateTime']
    src = request.form['src']

    app.logger.debug('url:' + url)
    msg = ds.addMystockFavor(code,title,url,dateTime,src)

    return jsonify(msg=msg)

@blueprint.route('/removeFavoriate', methods=['GET', 'POST'])
def removeFavoriate():
    id = request.form['id']
    ds.removeMystockFavor(id)
    return jsonify(msg="true")

@blueprint.route('/favorList/<code>', methods=['GET'])
def favorList(code):
    mynews = ds.getMyStockNews(code[2:])
    sdata = []
    for ne in mynews:
        sdata.append({
            'id': ne.id,
            'url': ne.url,
            'title': ne.title,
            'pub_date': ne.pub_date.strftime('%Y-%m-%d'),
            'src_type': ne.src_type
        })
    return jsonify(sdata)
