"""
    Add any handlers that you need here.  A global 
    application object 'app' will be made available to this
    file at runtime.
    Some base set of functionality will be provided by the
    framework.  In addition to running the app in both debug
    and production modes, standard routes such as diagnostic
    and version routes will be added.
"""
@app.route("/help", methods=["GET"])
def helper():
    return "you've been helped"
