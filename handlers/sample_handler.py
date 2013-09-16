from pyserver.core import app

@app.route("/hello", methods=["GET"])
def howdy():
    return "World!"
