import os
import uuid
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

def get_temp_storage_path_for(key):
    return "%s.%s.tmp" % (get_storage_path_for(key), str(uuid.uuid4())[:2])

def store_it(key, data, content_type):
    def store(final_name):
        temp_name = get_temp_storage_path_for(key)
        with open(temp_name, "w+") as temp_file:
            temp_file.write("%s\n" % key)
            temp_file.write("%s\n" % content_type)
            temp_file.write(data)

        os.rename(temp_name, final_name)

    final_name = get_storage_path_for(key)
    try:
        store(final_name)
    except IOError, e:
        # we only handle directory existence failure
        if e.errno != 2:
            raise
        try:
            os.makedirs(os.path.split(final_name)[0])
        except OSError, mde:
            # someone else may have already created the dir, so
            # if it's not an already exists, we have a problem
            if not mde.errno == 17:
                raise
        store(final_name)

def read_it(key):
    def read():
        with open(get_storage_path_for(key)) as f:
            key_from_file = f.readline().strip()
            if not key == key_from_file:
                raise Exception("bad data file, expected key %s got %s" % (key, key_from_file))
            content_type = f.readline().strip()
            return content_type, f.read()
    try:
        return read()
    except IOError, e: 
        # no file, return nothing
        if e.errno == 2:
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
    store_this_content_type = request.content_type
    store_this = None
    if request.json:
        store_this = json.dumps(request.json)
    elif request.data: 
        store_this = request.data

    if not store_this and request.values.to_dict:
        # for form data we're going to conveniently store it as a json
        # blob, so it can be easily parsed when retrieved
        data = request.values.to_dict(flat=False)
        store_this = convert_types_in_dictionary(remove_single_element_lists(data))
        store_this = json.dumps(store_this)
        store_this_content_type = 'application/json'

    store_it(key, store_this, content_type=store_this_content_type)
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
