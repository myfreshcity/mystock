#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, Response, request, session, g, redirect, url_for, abort, \
    render_template, flash
from flask import json, jsonify, Blueprint, render_template
import pandas as pd
import time
import urllib
from webapp.services import db_service as ds,data_service as dts,holder_service as  hs
from webapp.models import MyStock
from webapp import functions as fn
from flask import current_app as app

blueprint = Blueprint('stock', __name__)

@blueprint.route('/mystock/<code>', methods=['GET'])
def mystock(code):
    title = '自选股'
    if code == '1':
        data = dts.getMyStocks(code)
        title = '备选股'
    elif code == '0':
        data = dts.getMyStocks(code)
        title = '自选股'
    else:
        data = dts.getMyStocks(code)
        title = '相关股'

    return render_template('stock/mystock_list.html', title=title, code=code, stocks=result_list_to_array(data))

def result_list_to_array(data):
    sdata = []
    for index, row in data.iterrows():
        sdata.append(
            {'name': row['name'],
             'code': row.code,
             'grow_type': row.grow_type,
             'ncode': fn.code_to_ncode(row.code),
             'pcode': row['code'] + ('01' if row['code'][:2] == '60'else '02'),
             'price': row.close,
             'mvalue': round(row.t_cap / (10000 * 10000), 2),
             'pe': round(row.t_cap / (row.jlr_ttm * 10000), 2),
             'ps': round(row.t_cap / (row.zyysr_ttm * 10000), 2),
             'pcf': round(row.t_cap / (row.jyjxjl_ttm * 10000), 2),
             'pb': round(row.t_cap / (row.gdqy * 10000), 2),
             'roe': round(row.jlr_ttm * 100.0 / row.gdqy, 2),
             'dar': round(row.zfz * 100.0 / (row.zzc), 2),
             'jlr_rate': round(row['jlr_rate'] * 100.0, 2),
             'sh_rate': row['count'],
             'cash_rate': round((row['xjye']) * 10000 * 100.0 / row.t_cap, 2),  # 企业可支配现金，包含现金借款
             'trade_date': row.trade_date,
             'report_type': row.report_type
             }
        )
    return sdata

@blueprint.route('/person_stockholder_rank', methods=['GET'])
def person_stockholder_rank():
    data = hs.getStockHolderRank()
    sdata = []
    for index, row in data.iterrows():
        sdata.append({
            'name': row['name'],
            'code': row.code,
            'ncode': fn.code_to_ncode(row.code),
            'sum': row['sum'],
            'size': int(row['count']),
            'avg': round(row['avg'],3),
            'launch_date': row.launch_date
        })
    return render_template('stock/stockholder_rank.html', title='自然人持股排行', stocks=sdata)

@blueprint.route('/<code>', methods=['GET'])
def home(code):
    stock = ds.getStock(code[2:])
    price = stock.current_price
    #app.logger.info('stock current price is:'+stock.current_price)
    dateTime = pd.date_range(start='20001231', periods=15, freq='3M').to_series()
    date = [pd.to_datetime(str(value)).strftime('%Y-%m-%d') for value in dateTime]
    return render_template('stock/home.html', title=stock.name, mydate=date,code=code,price=price)

@blueprint.route('/holder/<code>', methods=['GET'])
def holder(code):
    stock = ds.getStock(code)
    return render_template('stock/holder.html', title=stock.name, stock=stock)


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
        try:
            tcp = row['t_cap']
            rclose = row['close']
            spe = 0 if row['jlr_ttm']== 0 else round(tcp/row['jlr_ttm'],2)
            sps = 0 if row['zyysr_ttm']== 0 else round(tcp/row['zyysr_ttm'],2)
            spcf = 0 if row['jyjxjl_ttm']== 0 else round(tcp/row['jyjxjl_ttm'],2)
            spb = 0 if row['gdqy'] == 0 else round(tcp / row['gdqy'], 2)
            tdate = row['trade_date'].strftime('%Y-%m-%d')
        except Exception, ex:
            app.logger.error(tcp)
            app.logger.error(row['jlr_ttm'])
            app.logger.error(ex)

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

@blueprint.route('/revenueJson', methods=['GET'])
def revenueJson():
    tableData = []
    yysr = [] #营业收入
    jlr = [] #净利润
    jyjxjl = [] #经营性净现金流
    yysr_rate = [] #营业收入
    jlr_rate = [] #净利润
    jyjxjl_rate = [] #经营性净现金流

    roe = [] #净资产收益率

    code = request.args.get('code')[2:]
    quarter = int(request.args.get('quarter'))
    if request.args.get('pType'):
        pType = int(request.args.get('pType'))
    else:
        pType = 0
    df = ds.get_quarter_stock_revenue(code, quarter,pType)

    for index, row in df.iterrows():
        report_type = row['report_type'].strftime('%Y-%m-%d')
        s_jyjxjl_rate =  round(row['jyjxjl_grow_rate'] * 100, 2)
        s_jlr_rate = round(row['jlr_grow_rate'] * 100, 2)
        s_yylr_rate = round(row['yylr_grow_rate'] * 100, 2)
        s_yysr_rate = round(row['zyysr_grow_rate'] * 100, 2)

        if pType==1:
            row_zyysr = row['zyysr_qt']
            row_jlr = row['jlr_qt']
            row_yylr = row['yylr_qt']
            row_jyjxjl = row['jyjxjl_qt']
        else:
            row_zyysr = row['zyysr']
            row_jlr = row['jlr']
            row_yylr = row['yylr']
            row_jyjxjl = row['jyjxjl']

        yysr.append([report_type, row_zyysr])
        jlr.append([report_type, row_jlr])
        jyjxjl.append([report_type, row_jyjxjl])

        yysr_rate.append([report_type,s_yysr_rate])
        jlr_rate.append([report_type, s_jlr_rate])
        jyjxjl_rate.append([report_type,s_jyjxjl_rate])
        roe.append([report_type.encode('utf-8'), round(row['roe'], 2)])


        tableData.append(
            [report_type,
             format(row_zyysr, ','),
             str(format(row_yylr, ','))+'/'+str(format(row_jlr, ',')),
             format(row_jyjxjl, ','),
             round(row_yylr * 100/row_zyysr, 2),
             round(row_jyjxjl * 100/row_yylr, 2),
             s_yysr_rate,
             str(s_yylr_rate)+'/'+str(s_jlr_rate),
             s_jyjxjl_rate
             ]
        )

    return jsonify(data={'yysr':yysr,'jlr':jlr,'jyjxjl':jyjxjl,'yysr_rate':yysr_rate,\
                         'jlr_rate':jlr_rate,'jyjxjl_rate':jyjxjl_rate,'roe':roe},tableData=tableData)


@blueprint.route('/add', methods=['GET', 'POST'])
def add():
    code = request.form['code']
    app.logger.debug('code:' + code)
    msg = ds.addMystock(code)
    if msg:
        return jsonify(msg=msg)
    else:
        dts.updateFinanceData(code)  # 更新财务数据
        dts.updateTradeData(code)  # 更新交易数据
        dts.global_bdf, dts.global_tdf, dts.global_fdf = (None, None, None)
    return jsonify(msg='true')

@blueprint.route('/add_relation', methods=['GET', 'POST'])
def add_relation():
    mcode = request.form['mcode']
    scode = request.form['scode']

    app.logger.debug('mcode:' + mcode +',scode:' +scode)
    msg = ds.addRelationStock(mcode,scode)
    if msg:
        return jsonify(msg=msg)
    return jsonify(msg='true')

@blueprint.route('/del_relation', methods=['GET', 'POST'])
def del_relation():
    mcode = request.form['mcode']
    scode = request.form['scode']

    app.logger.debug('mcode:' + mcode +',scode:' +scode)
    msg = ds.delRelationStock(mcode,scode)
    if msg:
        return jsonify(msg=msg)
    return jsonify(msg='true')

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
    return jsonify(msg='true',code=code)

@blueprint.route('/rollback', methods=['POST'])
def rollback():
    code = request.form['code']
    ds.rollbackStock(code)
    return jsonify(msg='true',code=code)

@blueprint.route('/del', methods=['POST'])
def hardRemove():
    code = request.form['code']
    ds.hardRemoveMystock(code)
    return jsonify(msg='true',code=code)

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