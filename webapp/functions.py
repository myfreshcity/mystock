#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib
import pandas as pd
import numpy as np
from urlparse import urlparse, urljoin

from flask import request, flash, redirect, url_for

def md5(password):
    return hashlib.md5(password).hexdigest()

def get_data_array(mydate,myvalue):
    return [mydate.encode('utf-8'), round(myvalue / 1000000, 2)]

def code_to_ncode(code):
    return 'sh' + code if code[:2] == '60'else 'sz' + code

def get_code(code):
    return code[2:] if len(code) >= 8 else code

def date2timestamp(dt):
    import time
    return int(time.mktime(dt.timetuple()))*1000

def make_cache_key(*args, **kwargs):
    """Dynamic creation the request url."""

    path = request.path
    args = str(hash(frozenset(request.args.items())))
    return (path + args).encode('utf-8')

def profile(func):
    def wrapper(*args, **kwargs):
        import time
        start = time.time()
        func(*args, **kwargs)
        end   = time.time()
        print 'COST: {}'.format(end - start)
    return wrapper

#离群值处理
def filter_extreme_MAD(series, n):  # MAD:中位数去极值
    median = series.quantile(0.5)
    new_median = ((series - median).abs()).quantile(0.50)
    max_range = median + n * new_median
    min_range = median - n * new_median
    return np.clip(series, min_range, max_range)


def filter_extreme_3sigma(series, n=3):  # 3 sigma
    mean = series.mean()
    std = series.std()
    max_range = mean + n * std
    min_range = mean - n * std
    return np.clip(series, min_range, max_range)


def filter_extreme_percentile(series, min=0.025, max=0.975):  # 百分位法
    series = series.sort_values()
    q = series.quantile([min, max])
    return np.clip(series, q.iloc[0], q.iloc[1])
