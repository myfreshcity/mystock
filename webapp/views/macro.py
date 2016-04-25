#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, Response, request, session, g, redirect, url_for, abort, \
    render_template, flash
from flask import json, jsonify, Blueprint, render_template
import pandas as pd
import time
import urllib
from webapp.services import db_service as ds
from webapp.models import MyStock
from flask import current_app as app

blueprint = Blueprint('macro', __name__)


@blueprint.route('/', methods=['GET'])
def index():
    return render_template('macro/index.html', title='宏观指标')