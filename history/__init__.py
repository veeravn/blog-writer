import azure.functions as func
import logging
import json
from services.cosmos_db import get_post_history

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.function_name(name="get_history")
@app.route(route="history/{post_id}", methods=["GET"])
def get_history_func(req: func.HttpRequest, post_id: str) -> func.HttpResponse:
    try:
        history = get_post_history(post_id)
        return func.HttpResponse(json.dumps(history), mimetype="application/json", status_code=200)
    except Exception as e:
        logging.exception("Error fetching post history")
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
