import os
import json
import apsw

class JSONStore(object):

    _create = 'CREATE TABLE IF NOT EXISTS json_store (json TEXT, [order] INTEGER, created TEXT DEFAULT CURRENT_TIMESTAMP)'
    _append = 'INSERT INTO json_store (json, [order]) VALUES (?,?)'
    _update = 'UPDATE json_store SET [order]=?, json=? WHERE rowid=?'
    _get = 'SELECT rowid, json FROM json_store WHERE rowid = ? ORDER BY rowid'
    _delete = 'DELETE FROM json_store WHERE rowid = ?'
    _scan = 'SELECT rowid, json FROM json_store ORDER BY rowid'

    def __init__(self, db_path):
        self.path = os.path.abspath(db_path)
        if not os.path.exists(os.path.dirname(self.path)):
            os.makedirs(os.path.dirname(self.path))
        self._exec_statement(self._create)

    def _exec_statement(self, sql, params=()):
        with self.get_conn() as conn:
            conn.cursor().execute(sql, params)

    def convert(self, data):
        if type(data) == dict:
            data = json.dumps(data)
        return data

    def get_conn(self):
        conn = apsw.Connection(self.path, vfs=os.environ.get("SQLITE_VFS", "unix-dotfile"))
        return conn
    
    def destroy(self):
        os.unlink(self.path)

    def append(self, data, order=0):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(self._append, [self.convert(data), order])
            return conn.last_insert_rowid()
    
    def update(self, id, data, order=0):
        self._exec_statement(self._update, [order, self.convert(data), id])

    def scan(self):
        with self.get_conn() as conn:
            entries = []
            cursor = conn.cursor()
            for row in cursor.execute(self._scan):
               entries.append({ zt[0][0]:zt[1] for zt in zip(cursor.getdescription(), row) }) 
        return entries
    
    def get(self, id):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            d = None
            for row in  cursor.execute(self._get, [id]):
                d = { zt[0][0]:zt[1] for zt in zip(cursor.getdescription(), row) }
            return d

    def delete(self, id):
        with self.get_conn() as conn:
            conn.cursor().execute(self._delete, [id])

