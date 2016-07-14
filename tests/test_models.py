import unittest
import time
from datetime import datetime
from webapp import app, db, config_app,register_blueprints
from webapp.services import db_service,data_service
from webapp.models import MyStock,Stock,data_item,Comment

class ModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        config_app(app, 'scriptfan.cfg')
        register_blueprints(app)
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        db.session.remove()
        self.app_context.pop()

    def test_valid_confirmation_token(self):
        #u = User(password='cat')
        #db.session.add(u)
        db.session.commit()
        #token = u.generate_confirmation_token()
        #self.assertTrue(u.confirm(token))

    def test_service(self):
        #c = db_service.addComment('abc1','abc1')

        #print(c.created_time.strftime('%Y-%m-%d'))
        #c = data_service.updateFinanceBasic('000418')
        c = data_service.updateTradeBasic('600000','sh')
