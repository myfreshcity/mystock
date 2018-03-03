#!/usr/bin/env python
# -*- coding: utf-8 -*-
import traceback

import math
from flask import Flask, Response, request, session, g, redirect, url_for, abort, \
    render_template, flash
from flask import json, jsonify, Blueprint, render_template
import pandas as pd
from webapp.extensions import cache
import time
import urllib

from flask_login import login_required,current_user

from webapp.services import getHeaders, db_service as ds,data_service as dts,holder_service as hs,ntes_service as ns,xueqiu_service as xues
from webapp.models import MyStock
from webapp import functions as fn
from flask import current_app as app

blueprint = Blueprint('stock', __name__)

@blueprint.route('/mystock/<code>', methods=['GET'])
@login_required
def mystock(code):
    if code == '1':
        stock = 'sh00000A'
        title = '备选股'
    elif code == '0':
        stock = 'sh00000A'
        title = '自选股'
    elif code == '2':
        stock = 'sh00000A'
        title = '所有股票'
    else:
        stock = code
        title = '相关股'

    return render_template('stock/mystock_list_v2.html', title=title, code=stock,stype=code)

@blueprint.route('/mystockJson', methods=['GET'])
def mystockJson():
    code = request.args.get('code')
    uid = current_user.id
    if code == '1':
        data = dts.getMyStocks(uid, code)
    elif code == '0':
        data = dts.getMyStocks(uid, code)
    else:
        data = dts.getMyStocks(uid, code)

    return jsonify(data={'tableData':result_list_to_array(data)})


def result_list_to_array(data):
    sdata = []

    def fixBadData(x):
        return '-' if math.isnan(x) else x

    for index, row in data.iterrows():
        sdata.append(
            {'name': row['name'],
             'code': row.code,
             'tag': row.tag if hasattr(row, 'tag') else '',
             'ncode': fn.code_to_ncode(row.code),
             'pcode': row['code'] + ('01' if row['code'][:2] == '60'else '02'),
             'price': fixBadData(row.close),
             'mvalue': fixBadData(round(row.t_cap / (10000 * 10000), 2)),
             'pe': fixBadData(round(row.t_cap / (row.jlr_ttm * 10000), 2)),
             'ps': fixBadData(round(row.t_cap / (row.zyysr_ttm * 10000), 2)),
             'pcf': fixBadData(round(row.t_cap / (row.jyjxjl_ttm * 10000), 2)),
             'pb': fixBadData(round(row.t_cap / (row.gdqy * 10000), 2)),
             'roe': fixBadData(round(row.jlr_ttm * 100.0 / row.gdqy, 2)),
             'dar': fixBadData(round(row.zfz * 100.0 / (row.zzc), 2)),
             'jlr_rate': fixBadData(round(row['jlr_rate'] * 100.0, 2)),
             'sh_rate': fixBadData(row['count']),
             'cash_rate': fixBadData(round(row.jyjxjl_ttm * 1.0 / row.jlr_ttm, 2)),  # 现金净利润比
             'report_type': '-' if pd.isnull(row.report_type) else row.report_type
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
    #price = stock.current_price
    #app.logger.info('stock current price is:'+stock.current_price)
    dateTime = pd.date_range(start='20001231', periods=15, freq='3M').to_series()
    date = [pd.to_datetime(str(value)).strftime('%Y-%m-%d') for value in dateTime]
    return render_template('stock/home.html', title='成长-'+stock.name, mydate=date,code=code)

@blueprint.route('/report/<code>', methods=['GET'])
def report(code):
    stock = ds.getStock(code[2:])
    #price = stock.current_price
    #app.logger.info('stock current price is:'+stock.current_price)
    dateTime = pd.date_range(start='20001231', periods=15, freq='3M').to_series()
    date = [pd.to_datetime(str(value)).strftime('%Y-%m-%d') for value in dateTime]
    return render_template('stock/report.html', title='财报-'+stock.name, mydate=date,code=code)

@blueprint.route('/info/<code>', methods=['GET'])
def info(code):
    mynews = []
    stock = ds.getStock(code[2:])
    if not current_user.is_anonymous:
        uid = current_user.id
        mynews = ds.getMyStockNews(uid,code[2:])
    return render_template('stock/info.html', title='资讯-'+stock.name, stock=stock,code=code,
                           news=mynews)

@blueprint.route('/cash/<code>', methods=['GET'])
def cash(code):
    stock = ds.getStock(code[2:])
    return render_template('stock/cash.html', title='现金-%s'%stock.name, stock=stock,code=code)

@blueprint.route('/holder/<code>', methods=['GET'])
def holder(code):
    stock = ds.getStock(code[2:])
    return render_template('stock/holder.html', title="股东-%s"%(stock.name), stock=stock,code=code)

@blueprint.route('/debet/<code>', methods=['GET'])
def debet(code):
    stock = ds.getStock(code[2:])
    return render_template('stock/debet.html', title='负债-'+stock.name, stock=stock,code=code)

@blueprint.route('/blog/<code>', methods=['GET'])
@login_required
def blog(code):
    cd = code[2:].strip()
    uid = current_user.id
    stock = ds.getMyStock(uid,cd)
    sname = '' if stock is None else stock.name
    #price = stock.current_price
    return render_template('stock/blog2.html', title='日志-'+sname, code=code)

@blueprint.route('/valuation/<code>', methods=['GET'])
def valuation(code):
    stock = ds.getStock(code[2:])
    #price = stock.current_price
    return render_template('stock/valuation.html', title='估值-'+stock.name, code=code)

@blueprint.route('/valuationJson', methods=['GET'])
@cache.cached(timeout=3600*24*7, key_prefix=fn.make_cache_key)
def valuationJson():
    code = request.args.get('code')
    period = int(request.args.get('period'))
    df = ds.getStockValuationN(code[2:],period)

    df['fpe'] = fn.filter_extreme_MAD(df['pe'], 10)
    df['fps'] = fn.filter_extreme_MAD(df['ps'], 10)
    df['fpcf'] = fn.filter_extreme_MAD(df['pcf'], 10)
    df['fpb'] = fn.filter_extreme_MAD(df['pb'], 10)

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
            spe = row['pe']
            sps = row['ps']
            spcf = row['pcf']
            spb = row['pb']
            tdate = row['trade_date'].strftime('%Y-%m-%d')
        except Exception, ex:
            app.logger.error(tcp)
            app.logger.error(row['jlr_ttm'])
            app.logger.error(traceback.format_exc())

        close.append([tdate,rclose])
        #pe.append([fn.date2str(row['trade_date']), spe])
        _td_stamp = fn.date2timestamp(row['trade_date'])
        pe.append([_td_stamp,row['fpe']])
        ps.append([_td_stamp, row['fps']])
        pcf.append([_td_stamp, row['fpcf']])
        pb.append([_td_stamp, row['fpb']])

        tableData.append(
            [tdate,
             rclose,
             row['pe'],
             row['ps'],
             row['pcf'],
             row['pb'],
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
    quarter = int(request.args.get('quarter')) if request.args.get('quarter') else None
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

        yysr.append([report_type, row['zyysr_ttm']])
        jlr.append([report_type, row['jlr_ttm']])
        jyjxjl.append([report_type, row['jyjxjl_ttm']])

        yysr_rate.append([report_type,s_yysr_rate])
        jlr_rate.append([report_type, s_jlr_rate])
        jyjxjl_rate.append([report_type,s_jyjxjl_rate])
        roe.append([report_type.encode('utf-8'), round(row['roe'], 2)])


        tableData.append(
            [report_type,
             round(row_zyysr/10000, 2),
             s_yysr_rate,
             round(row_jlr / 10000, 2),
             s_jlr_rate,
             round(row_jyjxjl/10000, 2),
             s_jyjxjl_rate,
             round(row_jyjxjl/row_jlr, 2),
             ]
        )

    return jsonify(data={'yysr':yysr,'jlr':jlr,'jyjxjl':jyjxjl,'yysr_rate':yysr_rate,\
                         'jlr_rate':jlr_rate,'jyjxjl_rate':jyjxjl_rate,'roe':roe},tableData=tableData)

@blueprint.route('/cashJson', methods=['GET'])
def cashJson():
    tableData = []
    yysr = [] #营业收入TTM
    jlr = [] #净利润TTM
    jyjxjl = [] #经营性净现金流TTM

    cash_live_rate = [] #现金支持率
    cash_produce_rate = [] #现金生产率
    cash_jlr_rate = []  #利润含现比
    jyjxjl_rate = [] #经营性净现金流

    xjye = []  # 期末现金余额
    xjjze_qt = []  # 现金净增加额
    jlr_qt = []  # 净利润净增加额
    jyjxjl_qt = []  # 经营性现金净增加额

    code = request.args.get('code')[2:]
    quarter = int(request.args.get('quarter'))
    if request.args.get('pType'):
        pType = int(request.args.get('pType'))
    else:
        pType = 0
    df = ds.get_quarter_stock_revenue(code, quarter,pType)

    i = 0

    for index, row in df.iterrows():
        i = i+1
        report_type = row['report_type'].strftime('%Y-%m-%d')

        s_jyjxjl_rate =  round(row['jyjxjl_grow_rate'] * 100, 2)
        s_cash_live_rate = round(row['xjye'] * 100/row['zyysr_ttm'], 2)
        s_cash_produce_rate = round(row['jyjxjl_ttm'] * 100/row['zyysr_ttm'], 2)

        yysr.append([report_type, row['zyysr_ttm']])
        jlr.append([report_type, row['jlr_ttm']])
        jyjxjl.append([report_type, row['jyjxjl_ttm']])

        jyjxjl_rate.append([report_type,s_jyjxjl_rate])
        cash_live_rate.append([report_type,s_cash_live_rate])
        cash_produce_rate.append([report_type, s_cash_produce_rate])
        cash_jlr_rate.append([report_type,
                              round(row['jyjxjl_ttm'] * 1.0 / row['jlr_ttm'], 2)])

        # 只取前10*4条数据图形显示
        if i <= 40:
            xjye.append([report_type,row['xjye']])
            xjjze_qt.append([report_type, row['xjjze_qt']])
            jlr_qt.append([report_type, row['jlr_qt']])
            jyjxjl_qt.append([report_type, row['jyjxjl_qt']])

        if pType==1:
            row_zyysr = row['zyysr_qt']
            row_jlr = row['jlr_qt']
            row_xjjze = row['xjjze_qt']
            row_jyjxjl = row['jyjxjl_qt']
        else:
            row_zyysr = row['zyysr']
            row_jlr = row['jlr']
            row_xjjze = row['xjjze']
            row_jyjxjl = row['jyjxjl']

        #自由现金流
        row_free_jyjxjl = row['jyjxjl']-row['tz_out_gdtz']+row['tz_in_gdtz']


        tableData.append(
            [report_type,
             round(row['xjye']/10000, 2),
             round(row_zyysr/10000, 2),
             round(row_xjjze/10000, 2),
             round(row_jyjxjl/10000, 2),
             s_jyjxjl_rate,
             round(row_free_jyjxjl / 10000, 2),
             round(row_free_jyjxjl*100 /row['jyjxjl'], 2),
             round(row_jyjxjl * 1.0/row_jlr, 2),
             round(row['jyjxjl_ttm'] * 1.0 / row['jlr_ttm'], 2)
             ]
        )

    return jsonify(data={'yysr':yysr,'jlr':jlr,'jyjxjl':jyjxjl,'cash_live_rate':cash_live_rate,\
                         'cash_produce_rate':cash_produce_rate,'cash_jlr_rate':cash_jlr_rate,\
                         'xjye':xjye,'xjjze_qt':xjjze_qt,'jlr_qt':jlr_qt,'jyjxjl_qt':jyjxjl_qt},\
                            tableData=tableData)

@blueprint.route('/query', methods=['GET'])
def query():
    query = request.args.get('query')

    df = ds.get_global_basic_data()
    df = df[(df['name'].str.contains(query)) | (df.index.str.contains(query))]
    result = []
    for index, row in df.iterrows():
        result.append(
            {'id': index, 'name': row['name'], 'ncode': fn.code_to_ncode(index)}
        )

    return jsonify(result=result)


@blueprint.route('/add', methods=['GET', 'POST'])
def add():
    uid = current_user.id
    code = request.form['code']
    cname = request.form['cname']
    flag = request.form['stype']

    app.logger.debug('code:' + code)
    msg = ds.addMystock(uid,code,cname,flag)
    if msg:
        return jsonify(msg=msg)
    data = dts.getMyStocks(uid, code, True)
    return jsonify(msg='true', stock=result_list_to_array(data)[0])

@blueprint.route('/add_relation', methods=['GET', 'POST'])
def add_relation():
    mcode = request.form['mcode']
    scode = request.form['scode']

    app.logger.debug('mcode:' + mcode +',scode:' +scode)
    uid = current_user.id
    msg = ds.addRelationStock(uid,mcode,scode)
    if msg:
        return jsonify(msg=msg)
    return jsonify(msg='true')

@blueprint.route('/del_relation', methods=['GET', 'POST'])
def del_relation():
    mcode = request.form['mcode']
    scode = request.form['scode']

    app.logger.debug('mcode:' + mcode +',scode:' +scode)
    uid = current_user.id
    msg = ds.delRelationStock(uid,mcode,scode)
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
    uid = current_user.id
    ds.updateStockInPrice(uid,code,price,in_date)
    return jsonify(msg='true')

@blueprint.route('/saveTag', methods=['POST'])
def saveTag():
    code = request.form['code']
    tag = request.form['tag']
    uid = current_user.id
    ds.updateStockTag(uid,code,tag)
    data = dts.getMyStocks(uid,code,True)
    return jsonify(msg='true',stock=result_list_to_array(data)[0])

@blueprint.route('/remove', methods=['POST'])
def remove():
    code = request.form['code']
    uid = current_user.id
    msg = ds.removeMystock(uid,code)
    if msg:
        return jsonify(msg=msg)
    return jsonify(msg='true',code=code)

@blueprint.route('/rollback', methods=['POST'])
def rollback():
    code = request.form['code']
    uid = current_user.id
    msg = ds.rollbackStock(uid,code)
    if msg:
        return jsonify(msg=msg)
    return jsonify(msg='true',code=code)

@blueprint.route('/del', methods=['POST'])
def hardRemove():
    code = request.form['code']
    uid = current_user.id
    ds.hardRemoveMystock(uid,code)
    #dts.clearCacheGetMyStocks('1')  # 清除备选股缓存
    return jsonify(msg='true',code=code)

@blueprint.route('/queryComments', methods=['GET', 'POST'])
def queryComments():
    code = str(request.form['code'])
    page = int(request.form['page'])

    uid = current_user.id
    (totalPage,result) = ds.queryComment(uid,code,page)
    data = []
    for x in result:
        data.append({
            'id' : x.id,
            'stock': x.stock,
            'pid': x.parent_id,
            'flag': x.ct_flag,
            'date':x.created_time.strftime('%Y-%m-%d'),
            'content':x.content
        })
    return jsonify(data=data,totalPage=totalPage)


@blueprint.route('/updateComment', methods=['GET', 'POST'])
def updateComment():
    code = request.form['code']
    cid = request.form['cid']
    cflag = request.form['flag']
    content = request.form['content']
    try:
        if cid == '':
            cid = "%d" % time.time()
        uid = current_user.id
        c = ds.updateComment(uid,code,cid,content,cflag)
        return jsonify(msg='true',
                       data={'pid':c.parent_id,'id': c.id, 'content': c.content,'date':c.created_time.strftime('%Y-%m-%d'),'flag': c.ct_flag}
                       )
    except Exception, ex:
        app.logger.error(ex)
        return jsonify(msg='false')