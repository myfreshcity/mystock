# -*- coding: utf-8 -*-
"""
    webapp
    ~~~~~~~~~~~~~~

    Module to initialize and config flask application.
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import os
from flask import Flask, render_template, abort, url_for, session
from views import home, stock, setting,macro
from services import db_service,db

app = Flask(__name__)

app.debug_log_format = '[%(levelname)s] %(message)s'
app.debug = True

# Configuration application
def config_app(app, config):
    app.logger.info('Setting up application...')

    app.logger.info('Loading config file: %s' % config)
    app.config.from_pyfile(config)

    app.logger.info('Setting up extensions...')
    db.init_app(app)
    #login_manager.init_app(app)

    @app.after_request
    def after_request(response):
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            abort(500)
        return response


def register_blueprints(app):
    app.logger.info('Register blueprints...')
    app.register_blueprint(home.blueprint,   url_prefix='')
    app.register_blueprint(setting.blueprint,  url_prefix='/setting')
    app.register_blueprint(stock.blueprint, url_prefix='/stock')
    app.register_blueprint(macro.blueprint, url_prefix='/macro')

