import azure.functions as func
import json
import logging
from services.blob_storage import load_preferences_from_blob, save_preferences_to_blob

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.function_name(name="get_preferences")
@app.route(route="preferences/{user_id}", methods=["GET"])
def get_preferences(req: func.HttpRequest, user_id: str) -> func.HttpResponse:
    try:
        prefs = load_preferences_from_blob(user_id)
        return func.HttpResponse(json.dumps(prefs), mimetype="application/json", status_code=200)
    except Exception as e:
        logging.exception("Error getting preferences")
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

@app.function_name(name="save_preferences")
@app.route(route="preferences/{user_id}", methods=["POST"])
def save_preferences(req: func.HttpRequest, user_id: str) -> func.HttpResponse:
    try:
        preferences = req.get_json()
        save_preferences_to_blob(user_id, preferences)
        return func.HttpResponse("Preferences saved", status_code=200)
    except Exception as e:
        logging.exception("Error saving preferences")
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
