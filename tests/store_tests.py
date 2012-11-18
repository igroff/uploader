import unittest
from pyserver.store import JSONStore
from uuid import uuid4

class StoreFixture(unittest.TestCase):
    def setUp(self):
        app.config['STORAGE_ROOT'] = "./test_output"
        app.config['TESTING'] = True
        self.store_name = str(uuid4())
        self.app = app.test_client()
        self.app.debug = True

    def tearDown(self):
        pass

    def test_store_data(self):
        data = dict(one=1, name="the name")
        response = self.app.post("/store/%s" % self.store_name, data=data)
        self.assertEqual(200, response.status_code)
        id = json.loads(response.data)['id']
        self.assertTrue(type(id) == int)


        response = self.app.get("/store/%s/%d" % (self.store_name, id))
        self.assertEqual(200, response.status_code)
        jr = json.loads(response.data)
        loaded_data = json.loads(jr['json'])
        self.assertEqual(1, loaded_data['one'])
        self.assertEqual("the name", loaded_data['name'])

    def test_update_and_list(self):
        data = dict(one=1, name="the name")
        response = self.app.post("/store/%s" % self.store_name, data=data)
        self.assertEqual(200, response.status_code)
        id = json.loads(response.data)['id']

        data['two'] = 2
        self.app.post("/store/%s/%d" % (self.store_name, id), data=data)
    

        response = self.app.get("/store/%s" % self.store_name)
        self.assertEqual(200, response.status_code)
        jr = json.loads(response.data)
        self.assertEqual(1, len(jr))
        data = json.loads(jr[0]['json'])
        self.assertEqual(1, data['one'])
        self.assertEqual(2, data['two'])
        self.assertEqual("the name", data['name'])

    def test_update_remove(self):
        data = dict(one=1, name="the name")
        response = self.app.post("/store/%s" % self.store_name, data=data)
        self.assertEqual(200, response.status_code)
        id = json.loads(response.data)['id']

        response = self.app.post("/store/%s/%d" % (self.store_name, id), data=dict(one='null'))
        self.assertEqual(200, response.status_code)
        
        response = self.app.get("/store/%s" % self.store_name)
        self.assertEqual(200, response.status_code)
        jr = json.loads(response.data)
        data = json.loads(jr[0]['json'])
        self.assertFalse('one' in data, data)
        self.assertEqual("the name", data['name'])

    def test_delete(self):
        data = dict(one=1, name="the name")
        response = self.app.post("/store/%s" % self.store_name, data=data)
        self.assertEqual(200, response.status_code)
        id = json.loads(response.data)['id']
        self.assertTrue(type(id) == int)


        response = self.app.delete("/store/%s/%d" % (self.store_name, id))
        self.assertEqual(200, response.status_code)
        response = self.app.get("/store/%s/%d" % (self.store_name, id))
        self.assertEqual(404, response.status_code)
