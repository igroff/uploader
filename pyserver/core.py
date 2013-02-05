#! /usr/bin/env python

import os
import sys
import json
from cache import FileSystemCache
import logging
import socket
from os import path

from flask import Flask, request
from flask import render_template, jsonify
from flask import g
from jinja2 import ChoiceLoader, FileSystemLoader
from argparse import ArgumentParser
from functools import wraps
from werkzeug import secure_filename
from werkzeug.http import http_date


STATIC_DIR = os.environ.get('STATIC_DIR', path.join(os.getcwd(), 'static'))
TEMPLATE_DIR = os.environ.get('TEMPLATE_DIR', path.join(os.getcwd(), 'templates'))
app = Flask(__name__, static_folder=STATIC_DIR, template_folder=TEMPLATE_DIR)

app.config['VERSION'] = os.environ.get('CURRENT_SHA', None)
app.config['X-HOSTNAME'] = os.environ.get('X_HOSTNAME', socket.gethostname())
app.config['BIND_INTERFACE'] = os.environ.get('BIND_INTERFACE', '127.0.0.1')
app.config['LOG_LEVEL'] = os.environ.get('LOG_LEVEL', 'WARNING')
app.config['HANDLER_FILE'] = os.environ.get('HANDLER_FILE', None)
app.config['USER_COOKIE_NAME'] = os.environ.get('USER_COOKIE_NAME', 'UCNID')
app.config['ROOT_STORAGE_PATH'] = os.environ.get("ROOT_STORAGE_PATH", "./storage")
app.config['CACHE_ROOT'] = os.environ.get('CACHE_ROOT', '%s/cache' % (app.config['ROOT_STORAGE_PATH']))
app.config['USE_RELOADER'] = os.environ.get('USE_RELOADER', 'True')
app.config['TEMPLATE_DIR'] = TEMPLATE_DIR

app.config['_CACHE'] = FileSystemCache(app.config['CACHE_ROOT'])
app.jinja_loader = ChoiceLoader([
        FileSystemLoader("./templates"),
        FileSystemLoader("./pyserver/templates")
    ])

logging.basicConfig(
    format='%(asctime)s [%(levelname)s]: %(message)s',
    stream=sys.stderr,
    level=app.config['LOG_LEVEL']
)

def get_storage_location(named):
    return path.join(app.config['ROOT_STORAGE_PATH'], named)

def remove_single_element_lists(d):
    new_dict = {}
    for key, value in d.items():
        if type(value) == list and len(value) == 1:
            new_dict[key] = value[0]
        else:
            new_dict[key] = value
    return new_dict

def try_run(this):
    try:
        return this()
    except:
        return None

def convert_into_number(value):
    as_number = try_run(lambda: int(value)) or try_run(lambda: float(value)) 
    if as_number or as_number == 0:
        return as_number
    else:
        return value

def convert_types_in_dictionary(this_dictionary):
    into_this_dictionary = {}
    for key, value in this_dictionary.items():
        if type(value) == dict:
            value = convert_types_in_dictionary(value)
        elif type(value) == list:
            value = convert_types_in_list(value)
        else:
            value = convert_into_number(value)
        into_this_dictionary[key] = value
    return into_this_dictionary

def convert_types_in_list(this_list):
    into_this_list = []
    for item in this_list:
        if type(item) == list:
            new_value = convert_types_in_list(item)
        elif type(item) == dict:
            new_value = convert_types_in_dictionary(item)
        else:
            new_value = convert_into_number(item)
        into_this_list.append(new_value)
    return into_this_list

def cache_my_response(vary_by=None, expiration_seconds=900):
    def cache_wrapper_decorator(f):
        @wraps(f)
        def cache_wrapper(*args, **kwargs):
            if not vary_by:
                cache_key = request.url
            else:
                from StringIO import StringIO
                key_buffer = StringIO()
                key_buffer.write(request.url)
                for vary_by_this in vary_by:
                    key_buffer.write("%s" % request.values.get(vary_by_this, ''))
                cache_key = key_buffer.getvalue()
            cr = app.config['_CACHE'].get_or_return_from_cache(
                cache_key,
                expiration_seconds,
                lambda: f(*args, **kwargs),
                force_refresh = request.values.get('_reload_cache', False)
            )
            resp = app.make_response(cr[1])
            if cr[0]:
                resp.headers['Expires'] = http_date(cr[0])
            return resp
        return cache_wrapper
    return cache_wrapper_decorator
            
def make_my_response_json(f):
    @wraps(f)
    def view_wrapper(*args, **kwargs):
        view_return = f(*args, **kwargs)
        if type(view_return) == dict:
            return json_response(**view_return)
        elif type(view_return) == list:
            return json_response(view_return)
        elif type(view_return) == int:
            return json_response(**dict(status_code=view_return))
        elif type(view_return) == str:
            return json_response(view_return)
        else:
            return json_response(**{})
    return view_wrapper

def json_response(*args, **kwargs):
    """ Creates a JSON response for the given params, handling the creation a callback wrapper
        if a callback is provided, and allowing for either a string arg (expected to be JSON)
        or kwargs to be passed formatted correctly for the response.
        Also sets the Content-Type of the response to application/json
    """
    content_type = "application/json";
    # if provided, use the status code otherwise default to 200
    status_code = kwargs.get('status_code', 200)
    # remove it so it doesn't end up in our response
    if 'status_code' in kwargs:
        del(kwargs['status_code'])

    callback = kwargs.get('callback', None) or request.values.get('callback', None)
    
    # we'll remove the callback if it was passed in kwargs, since we can 
    # get a callback from multiple places we check specifically for its 
    # presence
    if 'callback' in kwargs:
        del(kwargs['callback'])

    if args and type(args[0]) == list:
        response_string = json.dumps(args[0], indent=2)
    elif args:
        response_string = args[0]
    else:
        response_string = json.dumps(kwargs, indent=2)

    if callback:
        response_string = "%s(%s);" % (callback, response_string)
        content_type = "application/javascript";
        # I know it's sucky but many clients will fail on jsonp requests
        # that return a 404
        if status_code == 404:
            status_code = 200
        
    return (
        response_string,
        status_code,
        {"Content-Type": content_type, "Cache-Control": "no-cache", "Pragma": "no-cache"}
    )

def global_response_handler(response):
    response.headers['X-HOSTNAME'] = app.config['X-HOSTNAME']
    response.headers['X-APP-VERSION'] = app.config['VERSION']
    return response

def global_request_handler():
    # this needs to be safe for use by the app
    g.user_token = secure_filename(request.cookies.get(app.config['USER_COOKIE_NAME'], 'DEFAULT'))

app.process_response = global_response_handler    
app.preprocess_request = global_request_handler

################################################################################
# views 

@app.route("/", methods=["GET"])
@app.route("/diagnostic", methods=["GET"])
@make_my_response_json
def diagnostic_view():
    """
        Used to return the status of the application, including the version
        of the running application.
    
        :statuscode 200: returned as long as all checks return healthy
        :statuscode 500: returned in the case of any diagnostic tests failing
    """
    return dict(message="ok",
        version=app.config['VERSION'],
        uid=g.user_token
    )

@app.route("/diagnostic/echo", methods=["GET"])
@make_my_response_json
def diagnostic_echo_view():
    """
        Helper endpoint for developing diagnostic checks.  Simply echoes back 
        any values provided in the inbound request.
    
        :param '*': any inbound request parameters will be echoed back
        :statuscode 200: always returns OK
    """
    return request.values.to_dict()

@app.route("/diagnostic/fail", methods=["GET"])
def fail():
    """ This endpoint is designed to show how the application fails.  Can be used
        to assist in creating monitors to check the application health and respond
        to failures.

        :statuscode 500: always returns failure
    """
    raise Exception("Test exception so you know how the app behaves")

# end views 
################################################################################

@app.errorhandler(500)
def general_error_handler(error):
    logging.error("unhandled exception: %s" % error)


if app.config['HANDLER_FILE']:
    logging.info("loading handlers from %s" % (app.config['HANDLER_FILE']))
    execfile(app.config['HANDLER_FILE'])
else:
    # find and load our handler files, this isn't fancy and it's not intended to be
    handler_list = [ "./handlers/%s" % (name) for name in os.listdir("./handlers")]
    handler_list.extend(
        [ "./pyserver/handlers/%s" % (name) for name in os.listdir("./pyserver/handlers")]
    )
    for file_path in handler_list:
        split_name = os.path.splitext(file_path)
        if split_name[1] == ".py" and not split_name[0] == "__init__":
            logging.info("loading handlers from %s" % (file_path))
            execfile(file_path)


if (__name__ == "__main__"):
    """ we should only get here for debugging and testing, as we're gonna
        use gunicorn for serving in production
    """
    arg_parser = ArgumentParser(description="")
    arg_parser.add_argument("-p", "--port", default=5000, type=int)
    arg_parser.add_argument("--host", default="127.0.0.1")
    arg_parser.add_argument("action", choices=('start', 'test', 'config'))
    args = arg_parser.parse_args()
    if args.action == "start":
        logging.getLogger().setLevel('DEBUG')
        app.run(
            host=args.host,
            use_reloader=(app.config['USE_RELOADER'] == 'True'),
            debug=True,
            use_debugger=True,
            port=args.port,
            extra_files=handler_list)
    elif args.action == "config":
        for key, value in app.config.items():
            print("%s: %s" % (key, value))
    else:
        import unittest
        import sys
        for name in os.listdir("./tests"):
            split_name = os.path.splitext(name)
            if "tests" in split_name[0] and split_name[1] == ".py":
                execfile(os.path.join("./tests", name))
        # unittest uses command line params, so remove ours
        sys.argv.pop()
        unittest.main() 
