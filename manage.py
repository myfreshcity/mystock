#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import os
from flask import Flask, render_template, abort, url_for, session
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager, Shell
from webapp import app, db, config_app,register_blueprints
from webapp.services import db_service as ds,data_service as dts,holder_service as hs

reload(sys)
sys.setdefaultencoding('utf8')

manager = Manager(app, with_default_commands=False)

def _make_context():
    return dict(app=app, db=db)

manager.add_command('shell', Shell(make_context=_make_context))

@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

@manager.command
def refresh():
    config_app(app, 'scriptfan.cfg')
    ctx = app.app_context()
    #ctx.push()
    hs.refreshStockHolder()
    print "hello"


@manager.option('-c', '--config', dest='config', help='Configuration file name', default='scriptfan.cfg')
@manager.option('-H', '--host',   dest='host',   help='Host address', default='0.0.0.0')
@manager.option('-p', '--port',   dest='port',   help='Application port', default=5000)
def runserver(config, host, port):
    config_app(app, config)
    register_blueprints(app)
    app.run(host=host, port=port,debug=True)

if __name__ == '__main__':
    manager.run()