# -*- coding: utf-8 -*-
"""
    webapp
    ~~~~~~~~~~~~~~

    Module to initialize and config flask application.
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys

from celery import Celery
from flask_login import current_user
from flask_principal import identity_loaded, RoleNeed, UserNeed

from webapp.views import holder

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import os
from flask import Flask, render_template, abort, url_for, session
from views import home, stock, setting,macro,detail
from services import db_service,db
from extensions import bcrypt, login_manager, principals, cache, admin_permission

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SECRET_KEY'] = 'super-secret'
app.config['SESSION_TYPE'] = 'filesystem'

app.debug_log_format = '[%(levelname)s] %(message)s'
app.debug = True

app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
# app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Configuration application
def config_app(app, config):
    app.logger.info('Setting up application...')

    app.logger.info('Loading config file: %s' % config)
    app.config.from_pyfile(config)

    app.logger.info('Setting up extensions...')
    db.init_app(app)
    # Init the Flask-Bcrypt via app object
    bcrypt.init_app(app)

    # Init the Flask-Login via app object
    login_manager.init_app(app)
    # Init the Flask-Prinicpal via app object
    principals.init_app(app)

    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender, identity):
        """Change the role via add the Need object into Role.

           Need the access the app object.
        """

        # Set the identity user object
        identity.user = current_user

        # Add the UserNeed to the identity user object
        if hasattr(current_user, 'id'):
            identity.provides.add(UserNeed(current_user.id))

        # Add each role to the identity user object
        if hasattr(current_user, 'roles'):
            for role in current_user.roles:
                identity.provides.add(RoleNeed(role.name))
    # 自定义全局函数
    app.add_template_global(admin_permission, 'admin_permission')
    app.add_template_global(app.config.get('VERSION_NO'), 'version_no')

    # Init the Flask-Cache via app object
    cache.init_app(app)


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
    app.register_blueprint(holder.blueprint, url_prefix='/holder')
    app.register_blueprint(setting.blueprint,  url_prefix='/setting')
    app.register_blueprint(stock.blueprint, url_prefix='/stock')
    app.register_blueprint(detail.blueprint, url_prefix='/detail')
    app.register_blueprint(macro.blueprint, url_prefix='/macro')

