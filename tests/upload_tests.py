import unittest
import sys
import unittest
import uuid
from StringIO import StringIO
from pyserver.core import *

uid = lambda: str(uuid.uuid4())

class UploadTestFixture(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.app_cache = app.config['_CACHE']
        self.app.debug = True

    def tearDown(self):
        app.config['_CACHE'] = self.app_cache

    def test_app_exists(self):
        self.assertTrue(self.app)

    def test_file_upload(self):
        pid = uid()
        fn = 'file_%s.txt' % (uid())
        r = self.app.post('/%s' % (pid),
            data={'file': (StringIO('my file contents'), fn)})
        self.assertEquals(200, r.status_code)
        self.assertTrue(fn in r.data)
        # does it come back when requested
        r = self.app.get('/%s/%s' % (pid, fn))
        self.assertTrue('my file contents' in r.data)

    def test_duplicate_file_upload(self):
        pid = uid()
        fn = 'file_%s.txt' % (uid())
        r = self.app.post('/%s' % (pid),
            data={'file': (StringIO('my file contents'), fn)})
        self.assertEquals(200, r.status_code)
        r = self.app.post('/%s' % (pid),
            data={'file': (StringIO('my file contents'), fn)})
        self.assertEquals(409, r.status_code)

    def test_non_existant_partition(self):
        """ this should always return a 200 even if there's nothing there """
        pid = uid()
        r = self.app.get("/list/%s" % (pid)) 
        self.assertEquals(200, r.status_code)
        self.assertTrue(pid in r.data)


