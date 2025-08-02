# routes/preferences.py
import azure.functions as func
import json
from function_app import app
from dao.blob_storage import load_preferences_from_blob, save_preferences_to_blob

@app.function_name(name="preferences")
@app.route(route="preferences/{user_id}", methods=["GET", "POST"])
def manage_preferences(req: func.HttpRequest) -> func.HttpResponse:
    user_id = req.route_params.get("user_id")
    try:
        if req.method == "GET":
            prefs = load_preferences_from_blob(user_id)
            return func.HttpResponse(json.dumps(prefs), mimetype="application/json", status_code=200)
        elif req.method == "POST":
            preferences = req.get_json()
            save_preferences_to_blob(user_id, preferences)
            return func.HttpResponse("Preferences saved", status_code=200)
        else:
            return func.HttpResponse("Method not allowed", status_code=405)
    except Exception as e:
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500)
