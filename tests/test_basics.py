import unittest
from flask import current_app
from webapp import app, db, config_app,register_blueprints


class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        config_app(app, 'scriptfan.cfg')
        register_blueprints(app)
        self.app_context = self.app.app_context()
        self.app_context.push()
        #db.create_all()

    def tearDown(self):
        db.session.remove()
        #db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        #self.assertTrue(current_app.config['TESTING'])
        pass
