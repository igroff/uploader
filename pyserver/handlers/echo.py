@app.route("/echo", methods=["GET", "POST"])
def echo_view():
    return str(request.headers.items())
