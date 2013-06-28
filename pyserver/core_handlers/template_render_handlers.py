import os
import json
from flask import send_file, request, render_template
from jinja2.exceptions import TemplateNotFound
from pyserver.core import app, convert_types_in_dictionary
from pyserver.core import remove_single_element_lists

HTML_CONTENT_TYPE_HEADER = {"Content-Type": "text/html"}
JSON_CONTENT_TYPE_HEADER = {"Content-Type": "application/json"}

@app.route("/raw_template/<path:template_path>")
def pyserver_core_template_render_handlers_return_template_at(template_path):
    """ Returns the unrendered contents of a template """
    return send_file(
            os.path.join(app.config['TEMPLATE_DIR'], template_path)
            )

@app.route("/render/<path:template_path>", methods=["GET", "POST"])
def pyserver_core_template_render_handlers_render_template_at(template_path):
    """ Given a request that contains data as either a json object,
        or in the body of the request, render the template requested.

        Currently supports templates with 

        :statuscode 200: successful rendering of the requested template
        :statuscode 404: requested template doesn't exist

    """
    callback = request.values.get('callback', None)

    if request.json:
        data = request.json
    else:
        # this allows us to recieve data passed in as part of the request
        # (non json) in a sensible manner
        data = request.values.to_dict(flat=False)
        data = convert_types_in_dictionary(remove_single_element_lists(data))

    # well default our rendering to html
    if template_path.endswith(".json"):
        render_response = render_json_template(template_path, data)
    else: 
        render_response = render_html_template(template_path, data)

    response_string, status, headers = render_response
    # if we have been requested to use a callback, we want to render the
    # response using the callbac, as well as setting the content type
    # correctly
    if callback:
        # if the response is not already json, we'll make it so
        if not ('Content-Type', 'application/json') in set(headers.iteritems()):
            response_string = json.dumps(response_string)
            headers['Content-Type'] = 'application/json'
        # wrap our json response string in the callback
        response_string = "%s(%s)" % (callback, response_string)

    return response_string, status, headers


def render_html_template(template_path, data):
    rendered_string = None
    # assume failure
    status = 500
    try:
        rendered_string = render_template(template_path, **data)
        status = 200
    except TemplateNotFound as e:
        rendered_string = "No Template %s" % template_path
        status = 404
    return (rendered_string, status, HTML_CONTENT_TYPE_HEADER)

def render_json_template(template_path, data):
    json_string = None
    # assume failure
    status = 500
    try:
        json_string = render_template(template_path, **data)
        status = 200
    except TemplateNotFound as e:
        json_string = json.dumps(dict(message="No Template %s" % template_path))
        status = 404
    return (json_string, status, JSON_CONTENT_TYPE_HEADER)
