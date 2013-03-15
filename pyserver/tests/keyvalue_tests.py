import unittest
import json
from uuid import uuid4
import os
from pyserver.core import *

uuid = lambda: str(uuid4())

class KVTestFixture(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.app.debug = True

    def test_no_value_exists(self):
        response = self.app.get("/kv/dummy")
        self.assertEquals(404, response.status_code)

    def test_no_value_exists_jsonp(self):
        response = self.app.get("/kv/dummy?callback=p")
        self.assertEquals(200, response.status_code)
        self.assertEquals('p({"message": "no data for key"});', response.data)

    def test_odd_content_type(self):
        key_path = "/kv/%s" % (uuid())
        response = self.app.post(key_path, data="some data", content_type="superpants")
        self.assertEquals(200, response.status_code)
        response = self.app.get(key_path)
        self.assertEquals(200, response.status_code)
        self.assertEquals("some data", response.data)
        self.assertEquals("superpants", response.content_type)

    # testing some of the common content types that are handled by flask
    def test_app_javascript_content_type(self):
        key_path = "/kv/%s" % (uuid())
        response = self.app.post(key_path, data="some data", content_type="application/javascript")
        self.assertEquals(200, response.status_code)
        response = self.app.get(key_path)
        self.assertEquals(200, response.status_code)
        self.assertEquals("some data", response.data)
        self.assertEquals("application/javascript", response.content_type)

    def test_app_json_content_type_invalid_json_doesnt_store(self):
        key_path = "/kv/%s" % (uuid())
        response = self.app.post(key_path, data="some data", content_type="application/json")
        self.assertEqual(400, response.status_code)
        response = self.app.get(key_path)
        self.assertEqual(404, response.status_code)


    def test_app_multipart_form_content_type_structured_data(self):
        key_path = "/kv/%s" % (uuid())
        response = self.app.post(key_path, data=dict(pants="blue"))
        self.assertEqual(200, response.status_code)
        response = self.app.get(key_path)
        self.assertEqual(200, response.status_code)
        jr = json.loads(response.data)
        self.assertEquals("blue", jr['pants'])
        self.assertEquals("application/json", response.content_type)

    def test_create_from_request_body(self):
        key_path = "/kv/%s" % (uuid())
        data = dict(one=1, two=2, name="pants")
        response = self.app.post(key_path, data=json.dumps(data), content_type="application/javascript")
        self.assertEqual(200, response.status_code)
        
        response = self.app.get(key_path)
        self.assertEqual(200, response.status_code)
        response_data = json.loads(response.data)
        self.assertEqual('application/javascript', response.content_type)
        self.assertEqual(1, response_data['one'], str(response_data))
        self.assertEqual(2, response_data['two'], str(response_data))
        self.assertEqual("pants", response_data['name'], str(response_data))

    def test_create_from_json(self):
        key_path = "/kv/%s" % (uuid())
        data = dict(one=1, two=2, name="pants")
        response = self.app.post(key_path, data=json.dumps(data), content_type="application/json")
        self.assertEqual(200, response.status_code)
        
        response = self.app.get(key_path)
        self.assertTrue(200, response.status_code)
        response_data = json.loads(response.data)
        self.assertEqual(1, response_data['one'], str(response_data))
        self.assertEqual(2, response_data['two'], str(response_data))
        self.assertEqual("pants", response_data['name'], str(response_data))

    def test_delete(self):
        data = dict(one=1, two=2, name="pants")
        key_path = "/kv/%s" % (uuid())
        self.assertEqual(404, self.app.get(key_path).status_code)
        self.assertEqual(200, self.app.post(key_path).status_code)
        self.assertEqual(200, self.app.get(key_path).status_code)
        self.assertEqual(200, self.app.delete(key_path).status_code)
        self.assertEqual(404, self.app.get(key_path).status_code)

    def test_concurrent(self):
        the_url_path = "/kv/myconcurrent_key"
        def do_get():
            get_result = self.app.get(the_url_path)
            # it's fine to get a 404, some concurrent reads may happen before the writes
            self.assertTrue(get_result.status_code == 200 or get_result.status_code == 404)
            if get_result.status_code == 200:
                self.assertEquals("here is some data", get_result.data)
        def do_post():
            post_result = self.app.post(the_url_path, data="here is some data", content_type="awesome")
            self.assertEquals(200, post_result.status_code)
            r = self.app.get(the_url_path)
            self.assertEquals(200, r.status_code)

        from multiprocessing import Process
        from threading import Thread
        ConcurrentThing = Thread
        all_concurrent_things = []
        for x in range(100): 
            g,p = ConcurrentThing(target=do_get), ConcurrentThing(target=do_post)
            all_concurrent_things.append(g)
            all_concurrent_things.append(p)
            p.start()
            g.start()

        for thread in all_concurrent_things:
            thread.join()

