import unittest
import os
import sys
from StringIO import StringIO
from pyserver.sqlite_store import SqliteStore
from uuid import uuid4
import apsw

class StoreFixture(unittest.TestCase):
    def setUp(self):
        self.root_storage_path = os.path.join(os.environ['ROOT_STORAGE_PATH'], 'sqlitestore')
        self.store_name = str(uuid4())
        self.out_buffer = StringIO()
        self.orig_stdout = sys.stdout
        sys.stdout = self.out_buffer
        self.echo_stdout = True
        self.archetype = dict(mname="text", mvalue="integer")

    def tearDown(self):
        sys.stdout = self.orig_stdout
        if self.echo_stdout and self.out_buffer.getvalue():
            print(self.out_buffer.getvalue())

    def test_only_first_creates(self):
        store = SqliteStore(os.path.join(self.root_storage_path, self.store_name), self.archetype)
        # if it were to fail, we'd get an exception
        store = SqliteStore(os.path.join(self.root_storage_path, self.store_name), self.archetype)

    def test_invalid_archetype(self):
        store = SqliteStore(os.path.join(self.root_storage_path, self.store_name), self.archetype)
        # if it were to fail, we'd get an exception
        store = SqliteStore(os.path.join(self.root_storage_path, self.store_name),
                dict(pants='text')
                )
        self.assertRaises(apsw.SQLError, lambda: store.insert(pants='blue'))

    def test_invalid_get_where(self):
        store = SqliteStore(os.path.join(self.root_storage_path, self.store_name), self.archetype)
        id = store.insert(mname="ian", mvalue=34)
        self.assertRaises(apsw.SQLError, lambda: store.get_where(dog="cocker"))

    def test_insert(self):
        store = SqliteStore(os.path.join(self.root_storage_path, self.store_name), self.archetype)
        id = store.insert(mname="ian", mvalue=34)
        loaded = store.get(id=id)
        self.assertEquals("ian", loaded['mname'])
        self.assertEquals(34, loaded['mvalue'])
        self.assertTrue('updated' in loaded)
        self.assertTrue('created' in loaded)
        self.assertTrue('id' in loaded)

    def test_all_has_correct_columns(self):
        store = SqliteStore(os.path.join(self.root_storage_path, self.store_name), self.archetype)
        id = store.insert(mname="ian", mvalue=34)
        loaded = store.all()[0]
        self.assertEquals("ian", loaded['mname'])
        self.assertEquals(34, loaded['mvalue'])
        self.assertTrue('updated' in loaded)
        self.assertTrue('created' in loaded)
        self.assertTrue('id' in loaded)

    def test_get_where(self):
        store = SqliteStore(os.path.join(self.root_storage_path, self.store_name), self.archetype)
        store.insert(mname="ian", mvalue=34)
        store.insert(mname="ian", mvalue=35)
        store.insert(mname="ian", mvalue=36)
        store.insert(mname="ian", mvalue=37)
        loaded = store.get_where(mvalue=36)[0]
        self.assertEquals("ian", loaded['mname'])
        self.assertEquals(36, loaded['mvalue'])
        
    def test_get_multi_where(self):
        store = SqliteStore(os.path.join(self.root_storage_path, self.store_name), self.archetype)
        store.insert(mname="ian", mvalue=34)
        store.insert(mname="ian", mvalue=36)
        store.insert(mname="chuck", mvalue=36)
        store.insert(mname="ian", mvalue=37)
        loaded = store.get_where(mvalue=36)
        self.assertEquals(2, len(loaded))
        self.assertEquals("ian", loaded[0]['mname'])
        self.assertEquals(36, loaded[0]['mvalue'])
        self.assertEquals("chuck", loaded[1]['mname'])
        self.assertEquals(36, loaded[1]['mvalue'])

    def test_get_all(self):
        store = SqliteStore(os.path.join(self.root_storage_path, self.store_name), self.archetype)
        store.insert(mname="ian", mvalue=34)
        store.insert(mname="ian", mvalue=36)
        store.insert(mname="chuck", mvalue=36)
        store.insert(mname="ian", mvalue=37)
        loaded = store.all()
        self.assertEquals(4, len(loaded))
        self.assertEquals("ian", loaded[0]['mname'])
        self.assertEquals(34, loaded[0]['mvalue'])
        self.assertEquals("ian", loaded[1]['mname'])
        self.assertEquals(36, loaded[1]['mvalue'])
        self.assertEquals("chuck", loaded[2]['mname'])
        self.assertEquals(36, loaded[2]['mvalue'])
        self.assertEquals("ian", loaded[3]['mname'])
        self.assertEquals(37, loaded[3]['mvalue'])

    def test_delete(self):
        store = SqliteStore(os.path.join(self.root_storage_path, self.store_name), self.archetype)
        id = store.insert(mname="ian", mvalue=34)
        loaded = store.get(id=id)
        self.assertEquals("ian", loaded['mname'])
        self.assertEquals(34, loaded['mvalue'])
        store.delete(id)
        self.assertFalse(store.get(id=id))
    
    def test_delete_where(self):
        store = SqliteStore(os.path.join(self.root_storage_path, self.store_name), self.archetype)
        store.insert(mname="ian", mvalue=34)
        store.insert(mname="ian", mvalue=36)
        store.insert(mname="chuck", mvalue=36)
        store.insert(mname="ian", mvalue=37)
        loaded = store.all()
        self.assertEquals(4, len(loaded))
        self.assertEquals("ian", loaded[0]['mname'])
        self.assertEquals(34, loaded[0]['mvalue'])
        self.assertEquals("ian", loaded[1]['mname'])
        self.assertEquals(36, loaded[1]['mvalue'])
        self.assertEquals("chuck", loaded[2]['mname'])
        self.assertEquals(36, loaded[2]['mvalue'])
        self.assertEquals("ian", loaded[3]['mname'])
        self.assertEquals(37, loaded[3]['mvalue'])
        store.delete_where(mname="ian")
        loaded = store.all()
        self.assertEquals(1, len(loaded))
        self.assertEquals(36, loaded[0]['mvalue'])
        self.assertEquals("chuck", loaded[0]['mname'])

    def test_get_page(self):
        store = SqliteStore(os.path.join(self.root_storage_path, self.store_name), self.archetype)
        store.insert(mname="ian", mvalue=34)
        store.insert(mname="ian", mvalue=36)
        store.insert(mname="chuck", mvalue=36)
        store.insert(mname="ian", mvalue=37)
        loaded = store.get_page(0, 2)
        self.assertEquals(2, len(loaded))
        self.assertEquals("ian", loaded[0]['mname'])
        self.assertEquals(34, loaded[0]['mvalue'])
        self.assertEquals("ian", loaded[1]['mname'])
        self.assertEquals(36, loaded[1]['mvalue'])
        loaded = store.get_page(1, 2)
        self.assertEquals(2, len(loaded))
        self.assertEquals("chuck", loaded[0]['mname'])
        self.assertEquals(36, loaded[0]['mvalue'])
        self.assertEquals("ian", loaded[1]['mname'])
        self.assertEquals(37, loaded[1]['mvalue'])
        loaded = store.get_page(2, 2)
        self.assertFalse(loaded)
        loaded = store.get_page(0, 3)
        self.assertEquals(3, len(loaded))
        self.assertEquals("ian", loaded[0]['mname'])
        self.assertEquals(34, loaded[0]['mvalue'])
        self.assertEquals("ian", loaded[1]['mname'])
        self.assertEquals(36, loaded[1]['mvalue'])
        self.assertEquals("chuck", loaded[2]['mname'])
        self.assertEquals(36, loaded[2]['mvalue'])
        loaded = store.get_page(1, 3)
        self.assertEquals(1, len(loaded))
        self.assertEquals("ian", loaded[0]['mname'])
        self.assertEquals(37, loaded[0]['mvalue'])

    def test_get_where_throws_with_too_many_kwargs(self):
        store = SqliteStore(os.path.join(self.root_storage_path, self.store_name), self.archetype)
        self.assertRaises(Exception, lambda: store.get_where(one=1, two=2))

    def test_delete_where_throws_with_too_many_kwargs(self):
        store = SqliteStore(os.path.join(self.root_storage_path, self.store_name), self.archetype)
        self.assertRaises(Exception, lambda: store.delete_where(one=1, two=2))


