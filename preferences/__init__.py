import azure.functions as func
import json
import logging
from dao.blob_storage import load_preferences_from_blob, save_preferences_to_blob


def main(req: func.HttpRequest) -> func.HttpResponse:
    method = req.method
    user_id = req.route_params.get("user_id")  # If your route is preferences/{user_id}

    if method == "GET":
        return get_preferences(req, user_id)
    elif method == "POST":
        return save_preferences(req, user_id)
    else:
        return func.HttpResponse("Method not allowed", status_code=405)


def get_preferences(req: func.HttpRequest, user_id: str) -> func.HttpResponse:
    try:
        prefs = load_preferences_from_blob(user_id)
        return func.HttpResponse(json.dumps(prefs), mimetype="application/json", status_code=200)
    except Exception as e:
        logging.exception("Error getting preferences")
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

def save_preferences(req: func.HttpRequest, user_id: str) -> func.HttpResponse:
    try:
        preferences = req.get_json()
        save_preferences_to_blob(user_id, preferences)
        return func.HttpResponse("Preferences saved", status_code=200)
    except Exception as e:
        logging.exception("Error saving preferences")
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
