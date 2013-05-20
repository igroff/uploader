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
        methods that are not going to block and thus don't get a BusyError.
    """
    @functools.wraps(f)
    def backed_off(*args, **kwargs):
        e = None
        for i in range(12):
            try:
                return f(*args, **kwargs)
            except apsw.SQLError, exc:
                # no column is always a problem
                if "no such column" in exc.message:
                    raise exc
                e = exc
            except apsw.IOError, exc:
                e = exc
            finally:
                # we'll just wait and try again
                time.sleep(math.pow(2, i) / 1000)
        if e:
            raise e
    return backed_off

class SqliteStore(object):

    _my_columns = frozenset(('order', 'created', 'updated'))
    _create = '''
CREATE TABLE store (
    %s,
    [order] INTEGER,
    created TEXT DEFAULT CURRENT_TIMESTAMP,
    updated TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TRIGGER update_trigger
AFTER UPDATE
ON store
FOR EACH ROW
BEGIN
    UPDATE store SET updated = CURRENT_TIMESTAMP;
END
'''
    _insert_with_id = 'INSERT INTO store (rowid, [order], %(col_names)s) VALUES (?,?,%(parameter_group)s)'
    _insert = 'INSERT INTO store ([order], %(col_names)s) VALUES (?,%(parameter_group)s)'
    _update = 'UPDATE store SET [order]=?, json=? WHERE rowid=?'
    _get = 'SELECT rowid as id, * FROM store WHERE rowid = ? ORDER BY rowid'
    _get_where = 'SELECT rowid as id, * FROM store WHERE %s = ?'
    _delete = 'DELETE FROM store WHERE rowid = ?'
    _delete_where = 'DELETE FROM store WHERE %s = ?'
    _all = 'SELECT rowid as id, * FROM store ORDER BY rowid'
    _get_page = 'SELECT rowid as id, * FROM store ORDER BY rowid LIMIT %d OFFSET %d'

    def __init__(self, db_path, archetype=None):
        if not archetype:
            raise Exception("You can't create a SqliteStore for null archetype")
        self.path = os.path.abspath("%s.s3db" % db_path)
        self.col_names = ",".join([key for key in archetype.keys()])
        self.parameter_group = ",".join(["?" for key in archetype.keys()])
        self._insert = self._insert % self.__dict__
        self._insert_with_id = self._insert_with_id % self.__dict__


        try:
            os.makedirs(os.path.dirname(self.path))
        except OSError, e:
            # if it's not just an already exists, raise
            if not e.errno == 17:
                raise e
        if not os.path.exists(self.path):
            try:
                create_stmt = self._create % ",\n".join(["%s %s" % (item[0], item[1].upper()) for item in archetype.items()])
                with self.get_conn() as conn:
                    conn.cursor().execute(create_stmt)
            except apsw.BusyError, e:
                # either someone has done it or is going to in this case
                pass

    def convert(self, data):
        if type(data) == dict:
            data = json.dumps(data)
        return data

    def get_conn(self, vfs=os.environ.get("SQLITE_VFS", "unix-dotfile")):
        conn = apsw.Connection(self.path, statementcachesize=0, vfs=vfs)
        # yes we're using timeout with busy backoff
        conn.setbusytimeout(1000)
        return conn
    
    def destroy(self):
        os.unlink(self.path)

    @busy_backoff
    def insert(self, id=None, order=0, **kwargs):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            values = [value for value in kwargs.values()]
            values.insert(0, order)
            if id:
                values.insert(0, id)
                cursor.execute(self._insert_with_id, values)
            else:
                cursor.execute(self._insert, values)
            return conn.last_insert_rowid()

    @busy_backoff
    def update(self, id, data, order=0):
        with self.get_conn() as conn:
            conn.cursor().execute(self._update, [order, self.convert(data), id])

    @error_backoff
    def all(self):
        with self.get_conn(vfs="unix-none") as conn:
            entries = []
            cursor = conn.cursor()
            for row in cursor.execute(self._all):
               entries.append({ zt[0][0]:zt[1] for zt in zip(cursor.getdescription(), row) }) 
        return entries

    @error_backoff
    def get(self, id):
        with self.get_conn(vfs="unix-none") as conn:
            cursor = conn.cursor()
            for row in  cursor.execute(self._get, [id]):
                return { zt[0][0]:zt[1] for zt in zip(cursor.getdescription(), row) }

    @error_backoff
    def get_page(self, page=0, size=10):
        limit = size
        offset = page * size
        with self.get_conn(vfs="unix-none") as conn:
            cursor = conn.cursor()
            d = []
            for row in  cursor.execute(self._get_page % (limit, offset)):
                d.append({ zt[0][0]:zt[1] for zt in zip(cursor.getdescription(), row) })
            return d
    
    @error_backoff
    def get_where(self, **kwargs):
        if len(kwargs) > 1:
            raise Exception("only supporting single column where clause at this time")
        with self.get_conn(vfs="unix-none") as conn:
            cursor = conn.cursor()
            d = []
            for row in  cursor.execute(self._get_where % kwargs.keys()[0], kwargs.values()):
                d.append({ zt[0][0]:zt[1] for zt in zip(cursor.getdescription(), row) })
            if len(d) ==1:
                return d[0]
            else:
                return d

    @busy_backoff
    def delete(self, id):
        with self.get_conn() as conn:
            conn.cursor().execute(self._delete, [id])

    @busy_backoff
    def delete_where(self, **kwargs):
        if len(kwargs) > 1:
            raise Exception("only supporting single column where clause at this time")
        with self.get_conn() as conn:
            conn.cursor().execute(self._delete_where % kwargs.keys()[0], kwargs.values())
