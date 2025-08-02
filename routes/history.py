# routes/history.py
import azure.functions as func
import json
from function_app import app
from dao.cosmos_db import get_all_posts_by_user, get_post_history_by_id


@app.route(route="posts/{user_id}", methods=["GET"])
@app.route(route="posts/{user_id}/{post_id}", methods=["GET"])
def post_history(req: func.HttpRequest) -> func.HttpResponse:
    user_id = req.route_params.get("user_id")
    post_id = req.route_params.get("post_id")

    try:
        if post_id:
            history = get_post_history_by_id(user_id, post_id)
            return func.HttpResponse(json.dumps({"history": history}), mimetype="application/json", status_code=200)
        else:
            posts = get_all_posts_by_user(user_id)
            return func.HttpResponse(json.dumps({"posts": posts}), mimetype="application/json", status_code=200)

    except Exception as e:
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500)
