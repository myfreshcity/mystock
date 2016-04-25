#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import (Blueprint, render_template, redirect,
                   flash, url_for, request)
from flask import json,jsonify,render_template

import pandas as pd
import time
from webapp.services import db_service as ds

blueprint = Blueprint('setting', __name__)

@blueprint.route('/', methods = ['GET'])
def index():
    data = ds.getItemDate()
    return render_template('/setting/index.html', title='设置',dataItems=data)

@blueprint.route('/update/<int:id>', methods = ['GET'])
def update(id):
    if id == 1:
        #获取最新财务数据
        ds.getLatestTradeData()
    elif id == 2:
        #获取最新交易数据
        ds.getLatestFinaceData()
        flash('You were logged out')
    return redirect(url_for('setting'))
