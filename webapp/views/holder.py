# -*- coding: utf-8 -*-

from flask import render_template, request, jsonify, current_app as app, Blueprint
from flask_login import current_user

from webapp import functions as fn
from webapp.services import data_service as dts, db_service as ds, holder_service as hs
from webapp.views.home import blueprint


blueprint = Blueprint('holder', __name__)

@blueprint.route('/<code>', methods=['GET'])
def holder(code):
    hname = hs.queryHolderName(code)
    return render_template('home/holder_stock.html', title='股东持股', hcode=code, hname=hname)


@blueprint.route('/findStock', methods = ['GET'])
def findStock():
    data = []
    if current_user.is_authenticated:
        uid = current_user.id
        data = ds.getMyHolderFavor(uid)
    return render_template('home/holder_find_stock.html', title='股东选股', data=data)


@blueprint.route('/findHolderJson', methods=['GET'])
def findHolderJson():
    skey = request.args.get('skey')
    result = []
    data = dts.findHolder(skey)
    for index, row in data.iterrows():
        result.append(
            {'code': row['holder_code'],
             'name': row['holder_name'],
             'type': row['holder_type'],
             'size': row['hold_size'],
             'date': row['report_date'].strftime('%Y-%m-%d'),
             })
    return jsonify(data={'tableData': result})


@blueprint.route('/findStockJson', methods=['GET'])
def findStockJson():
    skey = request.args.get('skey')

    result = []
    st_result = dts.findStocksByHolder(skey)

    def fixBadData(x):
        import math
        return '-' if math.isnan(x) else round(x,2)

    for r in st_result:
        report_date = r['report_date'].strftime('%Y-%m-%d')
        df = r['data']
        tableData = []
        for index, row in df.iterrows():
            tableData.append(
                {'name': row['name'],
                 'code': row.code,
                 'holder_name': row.holder_name,
                 'holder_code': row.holder_code,
                 'hold_length': row.hold_length,
                 'stock_industry': row.industry,
                 'ncode': fn.code_to_ncode(row.code),
                 'pcode': row['code'] + ('01' if row['code'][:2] == '60'else '02'),
                 'price': fixBadData(row.close),
                 'rate': fixBadData(row.rate),
                 'mvalue': fixBadData(round(row.hold_amt / (10000 * 10000), 2)),
                 'pe': fixBadData(row.pe),
                 'ps': fixBadData(row.ps),
                 'pcf': fixBadData(row.pcf),
                 'pb': fixBadData(row.pb),
                 'report_type': row.report_date.strftime('%Y-%m-%d')
                 }
            )
        result.append({"r_date": report_date, "data": tableData})

    return jsonify(data=result)


@blueprint.route('/addFavoriate', methods=['GET', 'POST'])
def addFavoriate():
    uid = current_user.id
    code = request.form['code']
    name = request.form['name']
    msg = ds.addMyHolderFavor(uid,code,name)
    return jsonify(action='addFav',msg=msg)

@blueprint.route('/removeFavoriate', methods=['POST'])
def removeFavoriate():
    uid = current_user.id
    hcode = request.form['code']
    result = ds.removeMyHolderFavor(uid,hcode)
    return jsonify(action='removeFav',msg=True)

@blueprint.route('/isFavoriate', methods=['GET'])
def isFavoriate():
    uid = current_user.id
    hcode = request.args.get('code')
    result = ds.isMyHolderFavorExist(uid,hcode)
    return jsonify(msg=result)


@blueprint.route('/favorList', methods=['GET'])
def favorList():
    uid = current_user.id
    mynews = ds.getMyHolderFavor(uid)
    sdata = []
    for ne in mynews:
        sdata.append({
            'id': ne.id,
            'code': ne.holder_code,
            'name': ne.holder_name,
            'created_time': ne.create_date.strftime('%Y-%m-%d'),
        })
    return jsonify(sdata)