import unittest
import sys
from StringIO import StringIO
from pyserver.store import JSONStore
from uuid import uuid4
from pyserver.core import *

class StoreFixture(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['LOCAL_EVENT_SOURCES'] = ''
        self.store_name = str(uuid4())
        self.app = app.test_client()
        self.app.debug = True
        self.out_buffer = StringIO()
        self.orig_stdout = sys.stdout
        sys.stdout = self.out_buffer
        self.echo_stdout = True

    def tearDown(self):
        sys.stdout = self.orig_stdout
        if self.echo_stdout and self.out_buffer.getvalue():
            print(self.out_buffer.getvalue())

    def test_store_data_with_local_events(self):
        app.config['LOCAL_EVENT_SOURCES'] = frozenset(['pyserver.core_handlers.store_handlers'])
        self.echo_stdout = False
        data = dict(one=1, name="the name")
        response = self.app.post("/store/%s" % self.store_name, data=data)
        self.assertEqual(200, response.status_code)
        id = json.loads(response.data)['id']
        self.assertTrue(type(id) == int)
        event = json.loads(self.out_buffer.getvalue())
        self.assertEquals('pyserver.core_handlers.store_handlers', event['source'])
        self.assertEquals('DEFAULT', event['user_token'])
        message = event['message']
        self.assertEquals('add', message['action'])
        self.assertEquals(self.store_name, message['store_name'])
        self.assertEquals('the name', message['data']['name'])
        self.assertEquals(1, message['data']['one'])

    def test_update_data_with_local_events(self):
        self.echo_stdout = False
        data = dict(one=1, name="the name")
        response = self.app.post("/store/%s" % self.store_name, data=data)
        self.assertEqual(200, response.status_code)
        id = json.loads(response.data)['id']
        self.assertTrue(type(id) == int)
        app.config['LOCAL_EVENT_SOURCES'] = frozenset(['pyserver.core_handlers.store_handlers'])
        response = self.app.post("/store/%s/%d" % (self.store_name, id), data=data)
        event = json.loads(self.out_buffer.getvalue())
        self.assertEquals('pyserver.core_handlers.store_handlers', event['source'])
        self.assertEquals('DEFAULT', event['user_token'])
        message = event['message']
        self.assertEquals('update', message['action'])
        self.assertEquals(self.store_name, message['store_name'])
        self.assertEquals('the name', message['data']['name'])
        self.assertEquals(1, message['data']['one'])

    def test_post_with_id_creates_with_local_events(self):
        app.config['LOCAL_EVENT_SOURCES'] = frozenset(['pyserver.core_handlers.store_handlers'])
        self.echo_stdout = False
        id = 388273
        data = dict(one=1, name="the name")
        response = self.app.post("/store/%s/%d" % (self.store_name, id), data=data)
        self.assertEqual(200, response.status_code)
        event = json.loads(self.out_buffer.getvalue())
        self.assertEquals('pyserver.core_handlers.store_handlers', event['source'])
        self.assertEquals('DEFAULT', event['user_token'])
        message = event['message']
        self.assertEquals('add', message['action'])
        self.assertEquals(self.store_name, message['store_name'])
        self.assertEquals('the name', message['data']['name'])
        self.assertEquals(1, message['data']['one'])

    def test_delete_with_local_events(self):
        data = dict(one=1, name="the name")
        response = self.app.post("/store/%s" % self.store_name, data=data)
        self.assertEqual(200, response.status_code)
        id = json.loads(response.data)['id']
        self.assertTrue(type(id) == int)
        app.config['LOCAL_EVENT_SOURCES'] = frozenset(['pyserver.core_handlers.store_handlers'])
        self.echo_stdout = False
        response = self.app.delete("/store/%s/%d" % (self.store_name, id))
        self.assertEqual(200, response.status_code)
        event = json.loads(self.out_buffer.getvalue())
        self.assertEquals('pyserver.core_handlers.store_handlers', event['source'])
        self.assertEquals('DEFAULT', event['user_token'])
        message = event['message']
        self.assertEquals('delete', message['action'])
        self.assertEquals(self.store_name, message['store_name'])
        self.assertEquals(id, message['id'])

    def test_store_data(self):
        data = dict(one=1, name="the name")
        response = self.app.post("/store/%s" % self.store_name, data=data)
        self.assertEqual(200, response.status_code)
        id = json.loads(response.data)['id']
        self.assertTrue(type(id) == int)


        response = self.app.get("/store/%s/%d" % (self.store_name, id))
        self.assertEqual(200, response.status_code)
        loaded_data = json.loads(response.data)
        self.assertEqual(1, loaded_data['one'])
        self.assertEqual(id, loaded_data['id'])
        self.assertFalse("rowid" in loaded_data)
        self.assertEqual("the name", loaded_data['name'])

    def test_post_with_id_creates(self):
        id = 388273
        data = dict(one=1, name="the name")
        response = self.app.post("/store/%s/%d" % (self.store_name, id), data=data)
        self.assertEqual(200, response.status_code)
        loaded_data = json.loads(response.data)
        response = self.app.get("/store/%s/%d" % (self.store_name, id))
        loaded_data = json.loads(response.data)
        self.assertEqual(1, loaded_data['one'])
        self.assertEqual(id, loaded_data['id'])
        self.assertFalse("rowid" in loaded_data)
        self.assertEqual("the name", loaded_data['name'])

    def test_store_data_inbound_json(self):
        data = dict(one=1, name="the name")
        response = self.app.post("/store/%s" % self.store_name, content_type="application/json", data=json.dumps(data))
        self.assertEqual(200, response.status_code)
        new_id = json.loads(response.data)['id']
        self.assertTrue(type(new_id) == int)
        response = self.app.get("/store/%s/%d" % (self.store_name, new_id))
        self.assertEqual(200, response.status_code)
        loaded_data = json.loads(response.data)
        self.assertEqual(1, loaded_data['one'])
        self.assertEqual(new_id, loaded_data['id'])
        self.assertFalse("rowid" in loaded_data)
        self.assertEqual("the name", loaded_data['name'])

    def test_get_non_existant_item(self):
        response = self.app.get("/store/%s/%s" % (self.store_name, 4838383))
        self.assertEqual(404, response.status_code)
        self.assertEqual("{}", response.data)
        self.assertTrue("Content-Type", "application/json")

    def test_get_non_existant_item_jsonp(self):
        response = self.app.get(
            "/store/%s/%s?callback=p" % (self.store_name, 48383728)
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual("p({});", response.data)

    def test_update_non_existant_item_jsonp(self):
        response = self.app.post(
            "/store/%s/%s?callback=p" % (self.store_name, 48383728),
            data=dict(something="value")
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual("p({});", response.data)

    def test_update_non_existant_item_is_allowed_at_all(self):
        response = self.app.post(
            "/store/%s/%d" % (self.store_name, 48383728),
            data=dict(something="value")
        )
        self.assertEqual(200, response.status_code)
        self.assertEquals("{}", response.data)

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
        self.assertEqual(1, len(jr), response.data)
        data = jr[0]
        self.assertEqual(1, data['one'])
        self.assertEqual(2, data['two'])
        self.assertEqual("the name", data['name'])

    def test_update_and_list_json(self):
        data = dict(one=1, name="the name")
        response = self.app.post(
            "/store/%s" % self.store_name,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(200, response.status_code)
        id = json.loads(response.data)['id']

        data['two'] = 2
        self.app.post(
            "/store/%s/%d" % (self.store_name, id),
            data=json.dumps(data),
            content_type='application/json'
        )
    

        response = self.app.get("/store/%s" % self.store_name)
        self.assertEqual(200, response.status_code)
        jr = json.loads(response.data)
        self.assertEqual(1, len(jr), response.data)
        data = jr[0]
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
        data = json.loads(response.data)[0]
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
