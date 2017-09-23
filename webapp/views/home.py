#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, Blueprint,Response, request, session, g, redirect, url_for, abort, \
    render_template, flash
from flask import json, jsonify, render_template
import pandas as pd
import time
from webapp.services import db_service as ds

blueprint = Blueprint('home', __name__)

@blueprint.route('/', methods = ['GET'])
def index():
    return render_template('index.html')


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    info = {}
    info['message_l'] = '填写并登录'
    info['m_name'] = 'logn'
    if request.method == 'POST':
        formc = {}
        formc['name_l'] = request.form.get('inputName')
        formc['psw_l'] = request.form.get('inputPsw')
        session['name'] = formc['name_l']
        return jsonify(msg='',status='200')
    return render_template('login.html', info=info)

@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    info = {}
    info['base_url'] = request.url_root
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
            return jsonify(msg='OK', status='200')
    return render_template('register.html', info=info)


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