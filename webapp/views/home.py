#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from flask import Flask, Blueprint,Response, request, session, g, redirect, url_for, abort, \
    render_template, flash
from flask import json, jsonify, render_template
import pandas as pd
from flask import current_app as app
from webapp.extensions import cache
from webapp import functions as fn
from flask_principal import Principal, Identity, AnonymousIdentity,identity_changed

from flask_login import login_required, login_user, logout_user,current_user

from webapp.services import db_service as ds

blueprint = Blueprint('home', __name__)

@blueprint.route('/', methods = ['GET'])
def index():
    title = '做你的投资私人秘书'
    rw = ds.get_random_warning()
    code = 'sh00000A'
    return render_template('index.html', info=rw, code=code,title=title)


@blueprint.route('/howto', methods = ['GET'])
def howto():
    title = '快速开始投资笔记'
    return render_template('howto.html',title=title)

@blueprint.route('/why', methods = ['GET'])
def why():
    title = '为什么要做投资笔记'
    return render_template('why.html',title=title)

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    info = {}
    info['m_name'] = session['name'] if 'name' in session else ''
    if request.method == 'POST':
        username = request.form.get('mobile')
        password = request.form.get('password')
        user = ds.queryUser(username)
        if (user is None):
            return jsonify(msg='该用户不存在', status='402')
        if not user.check_password(password):
            return jsonify(msg='错误的用户名或密码', status='401')
        user.last_login_time = datetime.now()

        session['name'] = username
        # Using the Flask-Login to processing and check the login status for
        # user. Remember the user's login status.
        remember = request.form.get('remember') == 'true'
        login_user(user, remember)

        # Tell Flask-Principal the identity changed
        identity_changed.send(app._get_current_object(),
                              identity=Identity(user.id))

        return jsonify(msg='OK',status='200')
    return render_template('login.html', info=info)

@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    info = {}
    if request.method == 'POST':
        username = request.form.get('mobile')
        password = request.form.get('password')
        user = ds.queryUser(username)
        if not (user is None):
            return jsonify(msg='该用户已存在',status='402')
        user = ds.addUser(username,password)
        if user is None:
            return jsonify(msg='抱歉，注册失败',status='400')
        else:
            session['name'] = username
            login_user(user, False)
            identity_changed.send(app._get_current_object(),
                                  identity=Identity(user.id))

            return jsonify(msg='OK', status='200')
    return render_template('register.html', info=info)

@blueprint.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('name')
    # Using the Flask-Login to processing and check the logout status for user.
    logout_user()
    identity_changed.send(
        app._get_current_object(),
        identity=AnonymousIdentity())
    return redirect(url_for('home.login'))


@blueprint.route('/test', methods = ['GET'])
def test():
    #data = [{'y': 728, 'x': '0'}, {'y': 824, 'x': '1'}, {'y': 224, 'x': '2'}]
    d = [{'one' : 1,'two':1},{'one' : 2,'two' : 2},{'one' : 3,'two' : 3},{'two' : 4}]
    df = pd.DataFrame(d,index=['a','b','c','d'],columns=['one','two'])
    #data = json.loads(s)
    #print data
    #js = json.dumps(data)
    #resp = Response(js, status=200, mimetype='application/json')
    #resp.headers['Link'] = 'http://luisrei.com'
	#resp.status_code = 200
    #return resp
    return render_template('test.html', title='test', boys=get_data('boys'),girls=get_data('girls'))

@blueprint.route('/query', methods = ['POST','GET'])
def query():
    error = None
    if request.method == 'POST':
        year = request.form['year']
        month = request.form['month']
        #flash('abc')
        app.logger.debug('year:'+year+",month:"+month)
    return render_template('test.html')


@blueprint.route('/stockList', methods=['GET'])
@blueprint.route('/stockList/<pageNum>')
def stockList(pageNum=None):

    pageSize = 200
    page = 0 if pageNum is None else int(pageNum)
    df = ds.get_global_basic_data()
    totalPages = int(df.index.size / pageSize);

    df = df[(page*pageSize+1):(page+1)*pageSize]

    data = []
    for index, row in df.iterrows():
        data.append({
            'code': index,
            'name': row['name'],
            'ncode': fn.code_to_ncode(index)
        })

    cuPage = 1 if page==0 else page

    return render_template('stock_list.html',title="股票清单",stocks=data,currentPage=cuPage,totalPages=totalPages)

@blueprint.route('/stockJson', methods=['GET'])
def stockJson():
    return jsonify(data='true')


@blueprint.route('/hello/')
@blueprint.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)


@blueprint.route('/api', methods = ['GET'])
def api():
    resp = Response(get_data(), status=200, mimetype='application/json')
    #resp.headers['Link'] = 'http://luisrei.com'
    #resp = jsonify(data)
	#resp.status_code = 200
    return resp

def get_data(category):
    df = ds.getUsers()
    #s = df.to_json(date_format='utf-8',orient='index')
    #d = json.loads(s)
    data = [{"x": date, "y": val} for date, val in zip(df['year'], df[category])]
    #data = json.loads(s)
    #print data
    js = json.dumps(data)
    return js