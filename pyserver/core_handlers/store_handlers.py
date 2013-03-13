import os
import json
import os.path
from pyserver.store import JSONStore
from pyserver.core import app, get_storage_location, make_my_response_json, emit_local_message
from pyserver.core import convert_types_in_dictionary, remove_single_element_lists
from flask import request, g


app.config['STORAGE_ROOT'] = os.environ.get('STORAGE_ROOT', get_storage_location("jstore"))
MESSAGE_SOURCE = __name__


def get_named_store(name):
    return JSONStore(os.path.join(app.config['STORAGE_ROOT'], g.user_token, name))
        
    
@app.route("/store/<store_name>", methods=['POST'])
@make_my_response_json
def pyserver_core_store_handlers_store_in(store_name):
    """
        Save the data provided within the named store. Each POST to this endpoint 
        referring to the same 'store_name' will append data a list referred to by 
        'store_name'.

        Data can be provided in one of two ways:
        
        JSON - if the mimetype of the request isapplication/json and the body
        contains valid json, the json object will be appended.

        Request Data - any data provided in the querystring or the body of the
        requrest as form data will be stored.  Any numeric data will be stored
        in such a way as to maintain its type.

        .. sourcecode:: sh

        curl http://store.example.com:5000/store/my_test_list --data "number=1" --data "name=pants"

        will return data such as

        { "id": 1, "number": 1, "name": "pants" }

        :statuscode 200: successsfully stored the data provided
        :statuscode 5xx: an error occurred while trying to store the provided data
        
    """
    if request.json:
        data = request.json
    else:
        data = request.values.to_dict(flat=False)
        data = convert_types_in_dictionary(remove_single_element_lists(data))
    store_response = dict(id=get_named_store(store_name).append(data))
    emit_local_message(MESSAGE_SOURCE, dict(action="add", store_name=store_name, data=data))
    return store_response

@app.route("/store/<store_name>/<int:id>", methods=['POST'])
@make_my_response_json
def pyserver_core_store_handlers_update(store_name, id):
    """ Updates the item identified by <id>, in store named <store_name>.  
        As a convenience, if the item specified by id DOES NOT already exist
        it will be added.
    """
    if request.json:
        data = request.json
    else:
        data = request.values.to_dict(flat=False)
        data = convert_types_in_dictionary(remove_single_element_lists(data))
    stored = get_named_store(store_name).get(id)
    action = None
    if stored:
        action = 'update'
        stored = json.loads(stored['json'])
        for key, value in data.items():
            if (value == None or value == 'null') and key in stored:
                del(stored[key])
            else:
                stored[key] = value
        get_named_store(store_name).update(id, stored)
    else:
        action = 'add'
        # we're allowing for an update with a non existant item
        # which will simply create the item with the given id
        get_named_store(store_name).append(data, id)

    emit_local_message(MESSAGE_SOURCE, dict(action=action, store_name=store_name, data=data))

@app.route("/store/<store_name>/<int:id>", methods=["GET"])
@make_my_response_json
def pyserver_core_store_handlers_get_item(store_name, id):
    """
        Returns the data stored in the list 'store_name' with the provided id, or
        an empty JSON object '{}' if an item with the associated id doesn't exist.

        Example:

        curl http://store.example.com:5000/store/my_test_list/1

        returns:
        { "id": 1, "number": 1, "name": "pants" }

        curl http://store.example.com:5000/store/my_test_list/1?callback=cb
        
        returns:
        cb({ "id": 1, "name": "pants", "number": 1 });

        :statuscode 200: item exists, and was returned
        :statuscode 200: item does NOT exist, but request included a 'callback'
                         parameter
        :statuscode 404: no item by the provided id was found, no callback provided

    """
    item = get_named_store(store_name).get(id)
    if item:
        combined = json.loads(item['json'])
        for key,value in item.items():
            if key == "rowid":
                combined['id'] = value
            elif not key == "json":
                combined[key] = value
    return combined if item else dict(status_code=404)

@app.route("/store/<store_name>", methods=["GET"])
@make_my_response_json
def pyserver_core_store_handlers_get_list(store_name):
    """
    .. sourcecode:sh

    curl http://store.example.com:5000/store/my_test_list
    [
      {
        "id": 1, 
        "number": 1, 
        "name": "pants"
      }
    ]
    """
    items = []
    for item in get_named_store(store_name).scan():
        combined = json.loads(item['json'])
        for key, value in item.items():
            if key == "rowid":
                combined['id'] = value
            elif not key == "json":
                combined[key] = value
        items.append(combined)
    return items

@app.route("/store/<store_name>/<int:id>", methods=["DELETE"])
@make_my_response_json
def pyserver_core_store_handlers_delete_item(store_name, id):
    get_named_store(store_name).delete(id)
    emit_local_message(MESSAGE_SOURCE, dict(action='delete', store_name=store_name, id=id))
