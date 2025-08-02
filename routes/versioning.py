# routes/versioning.py
import azure.functions as func
import json
from function_app import app
from services.versioning import revert_to_post_version, get_post_version_content

@app.function_name(name="revert")
@app.route(route="revert", methods=["POST"])
def revert_post(req: func.HttpRequest) -> func.HttpResponse:
    try:
        data = req.get_json()
        user_id = data.get("user_id")
        target_post_id = data.get("target_post_id")

        if not user_id or not target_post_id:
            return func.HttpResponse("Missing user_id or target_post_id", status_code=400)

        result = revert_to_post_version(user_id, target_post_id)
        return func.HttpResponse(json.dumps(result), mimetype="application/json", status_code=200)

    except Exception as e:
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500)

@app.function_name(name="compare")
@app.route(route="compare/{post_id}", methods=["GET"])
def compare_versions(req: func.HttpRequest) -> func.HttpResponse:
    post_id = req.route_params.get("post_id")
    version1 = req.params.get("version1")
    version2 = req.params.get("version2")

    if not (version1 and version2):
        return func.HttpResponse("Missing version parameters", status_code=400)

    try:
        content1 = get_post_version_content(post_id, int(version1))
        content2 = get_post_version_content(post_id, int(version2))

        return func.HttpResponse(
            json.dumps({
                "version1": version1, "content1": content1,
                "version2": version2, "content2": content2
            }),
            mimetype="application/json", status_code=200
        )

    except Exception as e:
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500)
