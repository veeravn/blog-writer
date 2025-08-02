# routes/revise.py
import azure.functions as func
import json
import logging
from function_app import app
from dao.blob_storage import load_preferences_from_blob
from services.openai_client import revise_blog_post
from services.versioning import revise_post_version

@app.function_name(name="revise")
@app.route(route="revise_post", methods=["POST"])
def revise_post(req: func.HttpRequest) -> func.HttpResponse:
    try:
        data = req.get_json()
        post_id = data.get("post_id")
        original = data.get("original")
        feedback = data.get("feedback")
        user_id = data.get("user_id")

        if not all([post_id, original, feedback, user_id]):
            return func.HttpResponse("Missing required fields", status_code=400)

        preferences = load_preferences_from_blob(user_id)
        revised = revise_blog_post(original, feedback, preferences)
        new_version_id = revise_post_version(post_id, revised, feedback)

        return func.HttpResponse(
            json.dumps({"revised_content": revised, "new_version_id": new_version_id}),
            mimetype="application/json", status_code=200
        )

    except Exception as e:
        logging.exception("Failed to revise post")
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500)
