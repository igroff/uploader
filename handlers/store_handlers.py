import os
from pyserver.store import JSONStore


app.config['STORAGE_ROOT'] = os.environ.get('STORAGE_ROOT', './store/')

def get_named_store(name):
    return JSONStore(os.path.join(app.config['STORAGE_ROOT'], g.user_token, name))
        
    
@app.route("/store/<store_name>", methods=['POST'])
@make_my_response_json
def store_in(store_name):
    data = request.values.to_dict(flat=False)
    data = convert_types_in_dictionary(remove_single_element_lists(data))
    return dict(id=get_named_store(store_name).append(data))

@app.route("/store/<store_name>/<int:id>", methods=['POST'])
@make_my_response_json
def update(store_name, id):
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
    item = get_named_store(store_name).get(id)
    return item if item else 404

@app.route("/store/list/<store_name>", methods=["GET"])
@make_my_response_json
def get_list(store_name):
    return get_named_store(store_name).scan()

@app.route("/store/<store_name>/<int:id>", methods=["DELETE"])
@make_my_response_json
def delete_item(store_name, id):
    get_named_store(store_name).delete(id)
    
