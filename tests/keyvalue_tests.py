import unittest
import json
import os


class KVTestFixture(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.app.debug = True

    def test_odd_content_type(self):
        response = self.app.post("/kv/my_key", data="some data", content_type="superpants")
        self.assertTrue(200, response.status_code)
        response = self.app.get("/kv/my_key")
        self.assertTrue(200, response.status_code)
        self.assertEquals("some data", response.data)
        self.assertEquals("superpants", response.content_type)

    def test_create_from_request_body(self):
        data = dict(one=1, two=2, name="pants")
        response = self.app.post("/kv/my_key", data=json.dumps(data), content_type="application/javascript")
        self.assertTrue(200, response.status_code)
        
        response = self.app.get("/kv/my_key")
        self.assertTrue(200, response.status_code)
        response_data = json.loads(response.data)
        self.assertEqual('application/javascript', response.content_type)
        self.assertEqual(1, response_data['one'], str(response_data))
        self.assertEqual(2, response_data['two'], str(response_data))
        self.assertEqual("pants", response_data['name'], str(response_data))

    def test_create_from_json(self):
        data = dict(one=1, two=2, name="pants")
        response = self.app.post("/kv/my_key", data=json.dumps(data), content_type="application/json")
        self.assertTrue(200, response.status_code)
        
        response = self.app.get("/kv/my_key")
        self.assertTrue(200, response.status_code)
        response_data = json.loads(response.data)
        self.assertEqual(1, response_data['one'], str(response_data))
        self.assertEqual(2, response_data['two'], str(response_data))
        self.assertEqual("pants", response_data['name'], str(response_data))

    def test_delete(self):
        data = dict(one=1, two=2, name="pants")
        response = self.app.post("/kv/my_key", data=data)
        self.assertTrue(200, response.status_code)
        response = self.app.get("/kv/my_key")
        self.assertTrue(200, response.status_code)
        response = self.app.delete("/my_key")
        self.assertTrue(200, response.status_code)
        response = self.app.get("/kv/my_key")
        self.assertTrue(404, response.status_code)

