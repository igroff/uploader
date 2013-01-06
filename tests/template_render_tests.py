import uuid
import unittest


class TemplateRenderTestFixture(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.app_cache = app.config['_CACHE']
        self.app.debug = True
    
    def tearDown(self):
        app.config['_CACHE'] = self.app_cache

    def test_html_template_no_data(self):
        pass

    def test_html_template_with_data(self):
        pass

    def test_html_template_with_callback(self):
        pass

    def test_json_template_no_data(self):
        pass 

    def test_json_template_with_data(self):
        pass

    def test_json_template_with_callback(self):
        pass
