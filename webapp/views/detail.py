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

blueprint = Blueprint('detail', __name__)

@blueprint.route('/peJson', methods=['GET'])
def peJson():
    code = request.args.get('code')
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

    valueDf = ds.get_quarter_stock_revenue(code,quarter)
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

@blueprint.route('/debetJson', methods=['POST'])
def debetJson():
    code = request.form['code']
    period = int(request.form['period'])
    df = ds.getStockValuationN(code,period)

    close = []
    pe = []
    tableData = []

    for index, row in df.iterrows():
        try:
            tcp = row['t_cap']
            rclose = row['close']
            spe = 0 if row['jlr_ttm']== 0 else round(tcp/row['jlr_ttm'],2)
            tdate = row['trade_date'].strftime('%Y-%m-%d')
        except Exception, ex:
            app.logger.error(tcp)
            app.logger.error(row['jlr_ttm'])
            app.logger.error(ex)

        close.append([tdate,rclose])
        pe.append([tdate,spe])

        tableData.append(
            [tdate,
             tcp,
             spe,
             row['jlr'],
             row['jlr_ttm'],
             0
             ]
        )
    return jsonify(data={'actual': close, 'valuation': pe, 'tableData':tableData},period=period)

@blueprint.route('/pcfJson', methods=['GET'])
def pcfJson():
    code = request.args.get('code')
    period = 5 #最近5年
    quarter = 4 #第4季度

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

    valueDf = ds.get_quarter_stock_revenue(code,quarter)
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
    quarter = 4 #第4季度

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

    valueDf = ds.get_quarter_stock_revenue(code,quarter)
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
