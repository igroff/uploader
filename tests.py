import unittest

class TestFixture(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_response_header_has_hostname(self):
        response = self.app.get("/diagnostic")
        self.assertTrue('X-HOSTNAME' in response.headers)
        self.assertTrue(response.headers['X-HOSTNAME']) 

    def test_diagnostic(self):
        response = self.app.get("/diagnostic")
        self.assertTrue(200, response.status_code)
        self.assertEquals("application/json", response.content_type)
        jr = json.loads(response.data)
        self.assertEqual("ok", jr['message'])

    def test_callback(self):
        response = self.app.get("/diagnostic/echo?callback=run_me&bare=true")
        self.assertEqual('run_me({"bare": "true"});', response.data);
    
    def test_no_callback(self):
        response = self.app.get("/diagnostic/echo?bare=true")
        self.assertEqual('{"bare": "true"}', response.data);

    def test_diagnostic_contains_version(self):
        response = self.app.get("/diagnostic")
        self.assertTrue("version" in response.data, response.data)

    def test_can_find_view_from_handler_file(self):
        response = self.app.get("/test_me")
        self.assertEqual("this is a test response", response.data)

    def test_view_returning_non_gets_handled_in_json_response(self):
        @app.route("/return_null", methods=["GET"])
        @make_my_response_json
        def null_view():
            return None

        response = self.app.get("/return_null")
        jr = json.loads(response.data)
        self.assertEqual({}, jr)

