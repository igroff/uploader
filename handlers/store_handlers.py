import os
import os.path
from pyserver.store import JSONStore


app.config['STORAGE_ROOT'] = os.path.join(os.environ.get('STORAGE_ROOT', '.'), "jstore")


def get_named_store(name):
    return JSONStore(os.path.join(app.config['STORAGE_ROOT'], g.user_token, name))
        
    
@app.route("/store/<store_name>", methods=['POST'])
@make_my_response_json
def store_in(store_name):
    """
        Save the data provided within the named store. Each POST to this endpoint 
        referring to the same 'store_name' will append data a list referred to by 
        'store_name'.

        Data can be provided in one of two ways:
        
        JSON - if the mimetype of the request isapplication/json and the body
            contains valid json, the json object will be appended.

        Request Data - any data provided in the querystring or the body of
            the requrest as form data will be stored.  Any numeric data will
            be stored in such a way as to maintain its type.

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
    return dict(id=get_named_store(store_name).append(data))

@app.route("/store/<store_name>/<int:id>", methods=['POST'])
@make_my_response_json
def update(store_name, id):
    if request.json:
        data = request.json
    else:
        data = request.values.to_dict(flat=False)
        data = convert_types_in_dictionary(remove_single_element_lists(data))
    stored = json.loads(get_named_store(store_name).get(id)['json'])
    for key, value in data.items():
        if (value == None or value == 'null') and key in stored:
            del(stored[key])
        else:
            stored[key] = value
    get_named_store(store_name).update(id, stored)

@app.route("/store/<store_name>/<int:id>", methods=["GET"])
@make_my_response_json
def get_item(store_name, id):
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
    return combined if item else 404

@app.route("/store/<store_name>", methods=["GET"])
@make_my_response_json
def get_list(store_name):
    """
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
def delete_item(store_name, id):
    get_named_store(store_name).delete(id)
    
