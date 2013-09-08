import unittest
from pyserver.core import *

class TemplateTestFixture(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.app_cache = app.config['_CACHE']
        self.app.debug = True
    
    def tearDown(self):
        app.config['_CACHE'] = self.app_cache
