"""
    Add any handlers that you need here.  A global 
    application object 'app' will be made available to this
    file at runtime.
    Some base set of functionality will be provided by the
    framework.  In addition to running the app in both debug
    and production modes, standard routes such as diagnostic
    and version routes will be added.

decorators:
    make_my_response_json - this decorator allows the view to simply
    return a dictionary object, and handles creating a response that is
    a well formatted JSON response with correct content type as well
    as support for JSONP
"""
@app.route("/test_me", methods=["GET"])
def im_here_for_testing():
    return "this is a test response"

