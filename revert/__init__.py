import azure.functions as func
import json
from services.versioning import revert_to_post_version

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        data = req.get_json()
        user_id = data.get("user_id")
        target_post_id = data.get("target_post_id")

        if not user_id or not target_post_id:
            return func.HttpResponse("Missing user_id or target_post_id", status_code=400)

        result = revert_to_post_version(user_id, target_post_id)
        return func.HttpResponse(json.dumps(result), mimetype="application/json", status_code=200)

    except Exception as e:
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
