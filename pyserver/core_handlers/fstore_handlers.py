import os
import uuid
import errno
import os.path
import hashlib
import logging
from flask import request, send_from_directory
from pyserver.core import app, get_storage_location

app.config['FSTORE_ROOT'] = os.environ.get('FSTORE_ROOT',  get_storage_location('fstore-service'))

def get_storage_path_for(path_to_file):
    return os.path.join(
        app.config['FSTORE_ROOT'],
        path_to_file
    ) 

def get_temp_storage_path_for(path_to_file):
    return "%s.%s.tmp" % (get_storage_path_for(path_to_file), str(uuid.uuid4())[:2])

def store_it(file_storage, path_to_file):
    def store(final_name):
        temp_name = get_temp_storage_path_for(path_to_file)
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
def pyserver_core_fs_store_data(path_to_file=None):
    store_it(request.files['file'], path_to_file)
    return "Thanks"

@app.route("/fs/<path:path_to_file>", methods=["GET"])
def pyserver_core_fs_get_data_for(path_to_file=None):
    try:
        stored_file_path = get_storage_path_for(path_to_file)
        return send_from_directory(os.path.dirname(stored_file_path),
                os.path.basename(stored_file_path))
    except IOError, e: 
        logging.debug(e)
        # no file, return nothing
        if e.errno == 2:
            return "No file by that name", 404
        else:
            raise

@app.route("/fs/<path:path_to_file>", methods=["DELETE"])
def pyserver_core_fs_delete_data_for(path_to_file=None):
    try:
        os.unlink(get_storage_path_for(path_to_file))
        return "Thanks"
    except IOError, e:
        if e.errno == 2:
            return "No file by that name", 404
        raise
