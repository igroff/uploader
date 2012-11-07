#! /usr/bin/env python

import os
import sys
import json
import logging
from os import path

from flask import Flask, request
from flask import render_template, jsonify
from argparse import ArgumentParser
from functools import wraps


app = Flask(__name__)
app.config['VERSION'] = os.environ.get('CURRENT_SHA', None)
app.config['X-HOSTNAME'] = os.environ.get('XHOSTNAME', '')
app.config['LOG_LEVEL'] = os.environ.get('LOG_LEVEL', 'WARNING')

logging.basicConfig(
    format='%(asctime)s [%(levelname)s]: %(message)s',
    stream=sys.stderr,
    level=app.config['LOG_LEVEL']
)

def make_my_response_json(f):
    @wraps(f)
    def view_wrapper(*args, **kwargs):
        return json_response(**f(*args, **kwargs))
    return view_wrapper

def json_response(*args, **kwargs):
    """ Creates a JSON response for the given params, handling the creation a callback wrapper
        if a callback is provided, and allowing for either a string arg (expected to be JSON)
        or kwargs to be passed formatted correctly for the response.
        Also sets the Content-Type of the response to application/json
    """
    # if provided, use the status code otherwise default to 200
    status_code = kwargs.get('status_code', 200)
    # remove it so it doesn't end up in our response
    if 'status_code' in kwargs:
        del(kwargs['status_code'])

    if args:
        response_string = args[0]
    else:
        response_string = json.dumps(kwargs)

    callback = request.values.get('callback', None)
    if callback:
        response_string = "%s(%s);" % (callback, response_string)
        
    return (
        response_string,
        status_code,
        {"Content-Type": "application/json", "Cache-Control": "Private"}
    )

def global_response_handler(response):
    response.headers['X-HOSTNAME'] = app.config['X-HOSTNAME']
    return response

app.process_response = global_response_handler    

################################################################################
# views 

@app.route("/diagnostic", methods=["GET"])
@make_my_response_json
def diagnostic_view():
    """
        Used to return the status of the application, including the version
        of the running application.
    
        :status 200: returned as long as all checks return healthy
        :status 500: returned in the case of any diagnostic tests failing
    """
    return dict(message="ok", version=app.config['VERSION'])

@app.route("/diagnostic/echo", methods=["GET"])
@make_my_response_json
def diagnostic_echo_view():
    """
        Helper endpoint for developing diagnostic checks.  Simply echoes back 
        any values provided in the inbound request.
    
        :status 200: always returns OK
    """
    d = request.values.to_dict()
    if 'callback' in d:
        del(d['callback'])
    return d

@app.route("/diagnostic/fail", methods=["GET"])
def fail():
    """
        This endpoint is designed to show how the application fails.  Can be used
        to assist in creating monitors to check the application health and respond
        to failures.

        :status 500: always returns failure
    """
    raise Exception("Test exception so you know how the app behaves")

# end views 
################################################################################

@app.errorhandler(500)
def general_error_handler(error):
    logging.error("unhandled exception: %s" % error)

# find and load our handler files, this isn't fancy and it's not intended to be
for name in os.listdir("."):
    split_name = os.path.splitext(name)
    if "handler" in split_name[0] and split_name[1] == ".py":
        execfile(name)


if (__name__ == "__main__"):
    """ we should only get here for debugging and testing, as we're gonna
        use gunicorn for serving in production
    """
    arg_parser = ArgumentParser(description="")
    arg_parser.add_argument("-p", "--port", default=5000, type=int)
    arg_parser.add_argument("action", choices=('start', 'test'))
    args = arg_parser.parse_args()
    if args.action == "start":
        logging.getLogger().setLevel('DEBUG')
        app.run(use_reloader=True, debug=True, use_debugger=True, port=args.port)
    else:
        import unittest
        import sys
        for name in os.listdir("."):
            split_name = os.path.splitext(name)
            if "tests" in split_name[0] and split_name[1] == ".py":
                execfile(name)
        # unittest uses command line params, so remove ours
        sys.argv.pop()
        unittest.main() 
