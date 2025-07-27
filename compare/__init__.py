import azure.functions as func
import json
from services.cosmos_db import get_post_version_content

def main(req: func.HttpRequest) -> func.HttpResponse:
    post_id = req.route_params.get("post_id")
    version1 = req.params.get("version1") or req.get_query_params().get("version1")
    version2 = req.params.get("version2") or req.get_query_params().get("version2")
    if not (version1 and version2):
        return func.HttpResponse("Missing version1 or version2 parameter", status_code=400)
    try:
        content1 = get_post_version_content(post_id, int(version1))
        content2 = get_post_version_content(post_id, int(version2))
        result = {
            "version1": version1,
            "content1": content1,
            "version2": version2,
            "content2": content2
        }
        return func.HttpResponse(
            json.dumps(result),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        return func.HttpResponse(str(e), status_code=500)
