import os
import json
import math
import time
import apsw
import functools

def busy_backoff(f):
    @functools.wraps(f)
    def backed_off(*args, **kwargs):
        e = None
        for i in range(12):
            try:
                return f(*args, **kwargs)
            except apsw.BusyError, exc:
                e = exc
                # we'll just wait and try again
                time.sleep(math.pow(2, i) / 1000)
        if e:
            raise e
    return backed_off

def error_backoff(f):
    """ This decorator helps retry methods when SQL or IO Errors occur this is for
        methods that are not going to block and thus don't get a busy.
    """
    @functools.wraps(f)
    def backed_off(*args, **kwargs):
        e = None
        for i in range(12):
            try:
                return f(*args, **kwargs)
            except apsw.SQLError, exc:
                e = exc
            except apsw.IOError, exc:
                e = exc
            finally:
                # we'll just wait and try again
                time.sleep(math.pow(2, i) / 1000)
        if e:
            raise e
    return backed_off

class JSONStore(object):

    _create = 'CREATE TABLE IF NOT EXISTS json_store (json TEXT, [order] INTEGER, created TEXT DEFAULT CURRENT_TIMESTAMP)'
    _append = 'INSERT INTO json_store (json, [order]) VALUES (?,?)'
    _insert_with_id = 'INSERT INTO json_store (rowid, json, [order]) VALUES (?,?,?)'
    _update = 'UPDATE json_store SET [order]=?, json=? WHERE rowid=?'
    _get = 'SELECT rowid, json FROM json_store WHERE rowid = ? ORDER BY rowid'
    _delete = 'DELETE FROM json_store WHERE rowid = ?'
    _scan = 'SELECT rowid, json FROM json_store ORDER BY rowid'

    def __init__(self, db_path):
        self.path = os.path.abspath(db_path)
        try:
            os.makedirs(os.path.dirname(self.path))
        except OSError, e:
            # if it's not just an already exists, raise
            if not e.errno == 17:
                raise e

        try:
            with self.get_conn() as conn:
                conn.cursor().execute(self._create)
        except apsw.BusyError, e:
            # either someone has done it or is going to in this case
            pass

    def convert(self, data):
        if type(data) == dict:
            data = json.dumps(data)
        return data

    def get_conn(self, flags=None, vfs=os.environ.get("SQLITE_VFS", "unix-dotfile")):
        conn = apsw.Connection(self.path, statementcachesize=0, vfs=vfs)
        # yes we're using timeout with busy backoff
        conn.setbusytimeout(1000)
        return conn
    
    def destroy(self):
        os.unlink(self.path)

    @busy_backoff
    def append(self, data, id=None, order=0):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            if id:
                cursor.execute(self._insert_with_id, [id, self.convert(data), order])
            else:
                cursor.execute(self._append, [self.convert(data), order])
            return conn.last_insert_rowid()

    @busy_backoff
    def update(self, id, data, order=0):
        with self.get_conn() as conn:
            conn.cursor().execute(self._update, [order, self.convert(data), id])

    @error_backoff
    def scan(self):
        with self.get_conn(vfs="unix-none") as conn:
            entries = []
            cursor = conn.cursor()
            for row in cursor.execute(self._scan):
               entries.append({ zt[0][0]:zt[1] for zt in zip(cursor.getdescription(), row) }) 
        return entries

    @error_backoff
    def get(self, id):
        with self.get_conn(vfs="unix-none") as conn:
            cursor = conn.cursor()
            d = None
            for row in  cursor.execute(self._get, [id]):
                d = { zt[0][0]:zt[1] for zt in zip(cursor.getdescription(), row) }
            return d

    @busy_backoff
    def delete(self, id):
        with self.get_conn() as conn:
            conn.cursor().execute(self._delete, [id])

