import azure.functions as func
import json
from dao.cosmos_db import get_all_posts_by_user, get_post_history_by_id

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        user_id = req.route_params.get("user_id")
        post_id = req.route_params.get("post_id")

        if post_id:
            # Get complete version history for the specified post
            history = get_post_history_by_id(user_id, post_id)
            return func.HttpResponse(
                json.dumps({"history": history}),
                mimetype="application/json",
                status_code=200
            )
        else:
            # Get all posts for the user
            posts = get_all_posts_by_user(user_id)
            return func.HttpResponse(
                json.dumps({"posts": posts}),
                mimetype="application/json",
                status_code=200
            )
    except Exception as e:
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500)
