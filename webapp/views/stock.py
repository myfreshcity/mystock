#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask,Response,request, session, g, redirect, url_for, abort, \
     render_template, flash
from flask import json,jsonify,Blueprint,render_template
import pandas as pd
import time
from webapp.services import db_service as ds

blueprint = Blueprint('stock', __name__)

@blueprint.route('/', methods = ['GET'])
def index():
    return render_template('stock/index.html', title='股票')
