import azure.functions as func
import logging
import json
from dao.cosmos_db import get_post_history

def main(req: func.HttpRequest) -> func.HttpResponse:
    post_id = req.route_params.get("post_id")
    try:
        history = get_post_history(post_id)
        return func.HttpResponse(json.dumps(history), mimetype="application/json", status_code=200)
    except Exception as e:
        logging.exception("Error fetching post history")
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
