import os
import uuid
import errno
import os.path
import hashlib
from pyserver.core import app, get_storage_location

app.config['FSTORE_ROOT'] = os.environ.get('FSTORE_ROOT',  get_storage_location('fstore-service'))

def get_storage_path_for(path_to_file):
    return path.join(
        app.config['KVSTORE_ROOT'],
        path_to_file
    ) 

def get_temp_storage_path_for(path_to_file):
    return "%s.%s.tmp" % (get_storage_path_for(path_to_file), str(uuid.uuid4())[:2])

def store_it(file_storage, path_to_file):
    def store(final_name):
        temp_name = get_temp_storage_path_for(key)
        file_storage.save(temp_name)
        # atomic operation so we don't get partial writes
        # available for read
        os.rename(temp_name, final_name)

    final_name = get_storage_path_for(path_to_file)
    try:
        store(final_name)
    except (IOError, OSError), e:
        # we only handle directory existence failure
        if not e.errno == errno.ENOENT:
            # so, if it's something else:
            raise
        try:
            os.makedirs(os.path.split(final_name)[0])
        except OSError, mde:
            # someone else may have already created the dir, so
            # if it's not an already exists, we have a problem
            if not mde.errno == errno.EEXIST:
                raise
        store(final_name)


@app.route("/fs/<path:path_to_file>", methods=["POST"])
def store_data(path_to_file=None):
    store_it(request.files[0])
    return "Thanks", 200

@app.route("/fs/<path:path_to_file>", methods=["GET"])
def get_data_for(path_to_file=None):
    try:
        response.send_file(open(path_to_file))
    except IOError, e: 
        # no file, return nothing
        if e.errno == 2:
            return "No file by that name", 404
        else:
            raise

@app.route("/fs/<path:path_to_file>", methods=["DELETE"])
def delete_data_for(path_to_file=None):
    os.unlink(get_storage_path_for(path_to_file))
