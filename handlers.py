"""
    Add any handlers that you need here.  A global 
    application object 'app' will be made available in this context
    at runtime.

    Some base set of functionality will be provided by the
    framework.  In addition to running the app in both debug
    and production modes, standard routes such as diagnostic
    and version routes will be added.
    
    The framework also provides helpers around responding with JSON/JSONP
    as well as setting headers to provide assistance in identifying source
    servers.

    The framework also provides (via make) the automatic creation of
    documentation using sphinx and its autoflask extesion.  This leverages
    the view function docstrings when creating documentation so that the generated
    documentation will include the rollup of all the view docstrings mapped
    to their route data.

    e.g.
    GET /test_me

       this is my documentation for this endpoint

       Status Codes:
          * **200** -- returned if everything is ok

          * **500** -- returned if nothing is ok

decorators:
    make_my_response_json - this decorator allows the view to simply
    return a dictionary object, and handles creating a response that is
    a well formatted JSON response with correct content type as well
    as support for JSONP
"""
@app.route("/test_me", methods=["GET"])
def im_here_for_testing():
    """ this is my documentation for this endpoint

        :statuscode 200: returned if everything is ok
        :statuscode 500: returned if nothing is ok
    """

    return "this is a test response"

