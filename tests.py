import unittest

class TestFixture(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_diagnostic(self):
        response = self.app.get("/diagnostic")
        self.assertTrue(200, response.status_code)
        self.assertEquals("application/json", response.content_type)
        jr = json.loads(response.data)
        self.assertTrue(jr['version'] != None)
        self.assertEqual("ok", jr['message'])

