import unittest


class TestFixture(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.app.debug = True

    def test_response_header_has_hostname(self):
        response = self.app.get("/diagnostic")
        self.assertTrue('X-HOSTNAME' in response.headers)
        self.assertTrue(response.headers['X-HOSTNAME']) 
        
    def test_head_root_health_check(self):
        response = self.app.get("/")
        self.assertTrue(200, response.status_code)

    def test_diagnostic(self):
        response = self.app.get("/diagnostic")
        self.assertTrue(200, response.status_code)
        self.assertEquals("application/json", response.content_type)
        jr = json.loads(response.data)
        self.assertEqual("ok", jr['message'])

    def test_callback(self):
        response = self.app.get("/diagnostic/echo?callback=run_me&bare=true")
        self.assertEqual('run_me({\n  "bare": "true"\n});', response.data)
        self.assertEquals('application/javascript', response.content_type)
    
    def test_callback_alone(self):
        response = self.app.get("/diagnostic/echo?callback=run_me")
        self.assertEqual('run_me({});', response.data);

    def test_no_callback(self):
        response = self.app.get("/diagnostic/echo?bare=true")
        self.assertEqual('{\n  "bare": "true"\n}', response.data);

    def test_diagnostic_contains_version(self):
        response = self.app.get("/diagnostic")
        self.assertTrue("version" in response.data, response.data)

    @app.route("/test_me", methods=["GET"])
    def im_here_for_testing():
        """ this is my documentation for this endpoint

            :statuscode 200: returned if everything is ok
            :statuscode 500: returned if nothing is ok
        """

        return "this is a test response"

    def test_can_find_view_from_handler_file(self):
        response = self.app.get("/test_me")
        self.assertEqual("this is a test response", response.data)

    def test_view_returning_none_gets_handled_in_json_response(self):
        @app.route("/return_null", methods=["GET"])
        @make_my_response_json
        def null_view():
            return None

        response = self.app.get("/return_null")
        self.assertEqual(200, response.status_code)
        jr = json.loads(response.data)
        self.assertEqual({}, jr)

    def test_view_returning_dict_with_callback_in_request(self):
        @app.route("/bad_callback", methods=["GET"])
        @make_my_response_json
        def null_view():
            return dict(pants="blue")

        response = self.app.get("/bad_callback?callback=run_me")
        self.assertEquals(200, response.status_code)

    def test_static_works_at_all(self):
        if not os.path.exists("./static/"):
            os.makedirs("./static/")
        with open("./static/core_test_index.html", "w+") as sf:
            sf.write("I'm static!")
        response = self.app.get("/static/core_test_index.html")
        self.assertEqual(200, response.status_code)
        self.assertEqual("I'm static!", response.data.strip())
        if os.path.exists("./static/core_test_index.html"):
            os.unlink("./static/core_test_index.html")

    def test_convert_dictionary_simple(self):
        converted = convert_types_in_dictionary(dict(myint="1", myfloat="1.3"))
        self.assertEqual(1, converted['myint'])
        self.assertEqual(1.3, converted['myfloat'])
    
    @app.route("/convert", methods=["GET", "POST"])
    @make_my_response_json
    def convert():
        d = request.values.to_dict(flat=False)
        ret_val = convert_types_in_dictionary(remove_single_element_lists(d))
        return ret_val

    def test_convert_dictionary_request(self):
        response = self.app.get("/convert?myint=1&myfloat=1.3")
        self.assertEqual(200, response.status_code)
        converted = json.loads(response.data)
        self.assertEqual(1, converted['myint'])
        self.assertEqual(1.3, converted['myfloat'])

    def test_convert_dictionary_request_multiple(self):
        response = self.app.post("/convert?myint=2&myint=4")
        self.assertEqual(200, response.status_code)
        converted = json.loads(response.data)
        self.assertEqual([2,4], converted['myint'])

    def test_convert_dictionary_nested(self):   
        converted = convert_types_in_dictionary(
            dict(myint="1", myfloat="1.3", child=dict(childint="3"))
        )
        self.assertEqual(1, converted['myint'])
        self.assertEqual(1.3, converted['myfloat'])
        self.assertEqual(3, converted['child']['childint'])

    def test_convert_dictionary_nested_list(self):   
        converted = convert_types_in_dictionary(
            dict(myzero="0", myint="1", myfloat="1.3", child=dict(childint="3"), childlist=["1", 2])
        )
        self.assertEqual(0, convert_into_number("0"))
        self.assertEqual(0, converted['myzero'])
        self.assertEqual(1, converted['myint'])
        self.assertEqual(1.3, converted['myfloat'])
        self.assertEqual(3, converted['child']['childint'])
        self.assertEqual([1,2], converted['childlist'])


    @app.route("/return_list", methods=["GET", "POST"])
    @make_my_response_json
    def return_list():
        return [1,2,3]

    def test_return_list_json(self):
        response = self.app.get("/return_list")
        self.assertEqual(200, response.status_code)
        jr = json.loads(response.data)
        self.assertEqual([1,2,3], jr)

    @app.route("/can_return_status", methods=["GET", "POST"])
    @make_my_response_json
    def return_int():
        return 503 

    def test_can_return_statuscode(self):
        response = self.app.get("/can_return_status")
        self.assertEqual(503, response.status_code)
