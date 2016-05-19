#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import (Blueprint, render_template, redirect,
                   flash, url_for, request)
from flask import json,jsonify,render_template

import pandas as pd
import time
from webapp.services import data_service as dts,db_service as dbs

blueprint = Blueprint('setting', __name__)

@blueprint.route('/', methods = ['GET'])
def index():
    data = dbs.getItemDate()
    return render_template('/setting/index.html', title='设置',dataItems=data)

@blueprint.route('/update/', methods = ['GET','POST'])
def update():
    code = request.form['code']
    code = code[2:]
    flag = dts.updateFinanceBasic(code)
    return jsonify(msg=flag)
