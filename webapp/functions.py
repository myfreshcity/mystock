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