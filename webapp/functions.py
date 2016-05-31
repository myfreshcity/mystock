import hashlib
import pandas as pd
import numpy as np
from urlparse import urlparse, urljoin

from flask import request, flash, redirect, url_for

def md5(password):
    return hashlib.md5(password).hexdigest()

def get_data_array(mydate,myvalue):
    return [mydate.encode('utf-8'), round(myvalue / 1000000, 2)]