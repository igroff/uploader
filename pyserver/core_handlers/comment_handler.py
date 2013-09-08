from pyserver.core import app, make_my_response_json
from datetime import datetime

@app.route("/comment/<target_key>", methods=["POST"])
def add(target_key):
    return "add comment for %s" % target_key

@app.route("/comment/<comment_id>", methods=["PUT"])
def update(target_key):
    return "update comment for %s" % target_key

@app.route("/comment/<comment_id>", methods=["DELETE"])
def delete(comment_id):
    return "delete comment %s" % comment_id

@app.route("/comments/<target_key>", methods=["GET"])
def list_comments(target_key):
    return "get comments for %s" % target_key

@app.route("/comment/<comment_id>", methods=["GET"])
def get_comment(comment_id):
    return "get comment by id: %s" % comment_id
