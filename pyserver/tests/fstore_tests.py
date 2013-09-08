import unittest
from StringIO import StringIO
from uuid import uuid4
import json
import os
from pyserver.core import *

str_uuid = lambda: str(uuid4())


class FStoreTestFixture(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.app.debug = True

    def test_upload_at_all(self):
        contents = str_uuid()
        upload_data = (StringIO(contents), 'myfile.txt')
        data = {'file': upload_data}
        response = self.app.post("/fs/myfile.txt", data=data)
        self.assertEqual(200, response.status_code)
        self.assertEqual("Thanks", response.data)
        read_response = self.app.get("/fs/myfile.txt")
        self.assertEqual(200, read_response.status_code)
        self.assertEqual(contents, read_response.data)

    def test_upload_deeper_path_at_all(self):
        contents = str_uuid()
        upload_data = (StringIO(contents), '/root/child/myfile.txt')
        data = {'file': upload_data}
        response = self.app.post("/fs/root/child/myfile.txt", data=data)
        self.assertEqual(200, response.status_code)
        self.assertEqual("Thanks", response.data)
        read_response = self.app.get("/fs/root/child/myfile.txt")
        self.assertEqual(200, read_response.status_code)
        self.assertEqual(contents, read_response.data)

    def test_no_file_returns_404(self):
        response = self.app.get("/fs/some/path/that/shouldnt/exist.txt")
        self.assertEqual(404, response.status_code)

    def test_delete_at_all(self):
        contents = str_uuid()
        upload_data = (StringIO(contents), 'myfile.txt')
        data = {'file': upload_data}
        response = self.app.post("/fs/myfile.txt", data=data)
        self.assertEqual(200, response.status_code)
        self.assertEqual("Thanks", response.data)
        read_response = self.app.get("/fs/myfile.txt")
        self.assertEqual(200, read_response.status_code)
        self.assertEqual(contents, read_response.data)
        delete_response = self.app.delete("/fs/myfile.txt")
        self.assertEqual(200, delete_response.status_code)
