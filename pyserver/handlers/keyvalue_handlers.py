import os
import os.path
import hashlib

app.config['KVSTORE_ROOT'] = os.environ.get('KVSTORE_ROOT',  get_storage_location('kvstore-service'))

def get_storage_path_for(key):
    hash_o = hashlib.sha256()
    hash_o.update(key)
    storage_key = hash_o.hexdigest()
    return path.join(
        app.config['KVSTORE_ROOT'],
        storage_key[:2],
        storage_key[2:4],
        storage_key
    ) 

def store_it(key, data, content_type):
    def store():
        with open(get_storage_path_for(key), "w") as f:
            f.write("%s\n" % key)
            f.write("%s\n" % content_type)
            f.write(data)
    try:
        store()
    except IOError, e:
        os.makedirs(os.path.split(get_storage_path_for(key))[0])
        store()

def read_it(key):
    def read():
        with open(get_storage_path_for(key)) as f:
            if not key == f.readline().strip():
                raise Exception("bad data file")
            content_type = f.readline().strip()
            return content_type, f.read()
    try:
        return read()
    except IOError, e: 
        # no data, return nothing
        if not os.path.exists(get_storage_path_for(key)):
            return None, None
        else:
            raise
       
        

def delete_it(key):
    os.unlink(get_storage_path_for(key))

@app.route("/kv/<key>", methods=["POST"])
@make_my_response_json
def store_data(key=None):
    """
        Store all of the data provided in the body of the request, associated with the
        specified key.  The data stored includes the content type information of the request
        so on fetch the content type will be set as it was when the data was stored.

        :statuscode 200: provided data has been successfully stored by the given key
    """
    store_this = request.data
    store_it(key, request.data, content_type=request.content_type)
    return dict(message="ok")

@app.route("/kv/<key>", methods=["GET"])
def get_data_for(key=None):
    """
        For a given key return the data stored, if any.
    
        :statuscode 200: data found, and returned
        :statuscode 404: no stored data found for provided key
    """
    content_type, value = read_it(key)
    callback = request.values.get("callback", None)
    if not value:
        if callback:
            # this is specifically to handle the (most common) use case of JSONP blowing
            # chunks if the response is a 404 as the borwser will not do anything further
            # causing the callback in your javascript library to never fire
            return json_response(**dict(message="no data for key"))
        else:
            return json_response(**dict(message="no data for key", status_code=404))
    else:
        if callback:
            return ("%s(%s);" % (callback, value), 200, {"Content-Type": "application/javascript"})
        else:
            return (value, 200, {"Content-Type": content_type })

@app.route("/kv/<key>", methods=["DELETE"])
@make_my_response_json
def delete_data_for(key):
    """ 
        Removes all stored data for a given key.
    """
    delete_it(key)
    return dict(message="ok")
