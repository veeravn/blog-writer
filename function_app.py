import azure.functions as func
import logging
import json
import os
import tempfile
import uuid
from dao.blob_storage import (
    upload_file_to_blob, append_to_blob_batch, load_preferences_from_blob, save_preferences_to_blob, list_blob_files
)
from services.preprocess_data import preprocess_to_instruction_format
from services.openai_client import generate_blog_post, revise_blog_post
from services.versioning import (
    create_post_version, revise_post_version, revert_to_post_version
)
from dao.cosmos_db import get_post_by_id, get_post_version_content, get_all_posts_by_user, get_post_history_by_id
from services.memory import get_preferences
from services.continuous_finetune import continuous_finetune

# Set up Function App
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="ping", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def ping(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("pong")

@app.route(route="data-mgmt/list", methods=["GET"])
def list_all_files(req: func.HttpRequest) -> func.HttpResponse:
    """
    List all files in the datasets and batch containers.
    You can add ?container=datasets or ?container=batch to filter.
    """
    try:
        container = req.params.get("container", "datasets")  # default to 'datasets'
        files = list_blob_files(container)
        return func.HttpResponse(
            json.dumps({"files": files}),
            mimetype="application/json",
            status_code=200,
        )
    except Exception as e:
        logging.exception("Error listing files")
        return func.HttpResponse(
            json.dumps({"error": str(e)}), status_code=500, mimetype="application/json"
        )

@app.route(route="data-mgmt/batch", methods=["GET"])
def list_batch_files(req: func.HttpRequest) -> func.HttpResponse:
    """
    List all batch files (e.g., new_data.jsonl, archived batches) in the 'batch' container.
    """
    try:
        files = list_blob_files("batch")
        return func.HttpResponse(
            json.dumps({"files": files}),
            mimetype="application/json",
            status_code=200,
        )
    except Exception as e:
        logging.exception("Error listing batch files")
        return func.HttpResponse(
            json.dumps({"error": str(e)}), status_code=500, mimetype="application/json"
        )

@app.function_name(name="blog_post")   
@app.route(route="blog-post", methods=["POST"])
def generate_post(req: func.HttpRequest) -> func.HttpResponse:
    try:
        data = req.get_json()
        prompt = data.get("prompt", "").strip()
        user_id = data.get("user_id")
        style_reference_post_id = data.get("style_reference_post_id")
        style_description = data.get("style_description")
        structure = data.get("structure")

        style_text = None
        if style_reference_post_id:
            ref_post = get_post_by_id(style_reference_post_id)
            style_text = ref_post.get("content") if ref_post else None
        elif style_description:
            style_text = style_description

        preferences = get_preferences(user_id) if user_id else None
        result = generate_blog_post(prompt, style_text, preferences, structure)

        saved_post = create_post_version(user_id, prompt, result.get("full_text", ""))
        result["post_id"] = saved_post["id"]

        return func.HttpResponse(json.dumps(result), mimetype="application/json", status_code=200)

    except Exception as e:
        logging.exception("Error generating post")
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500)
    
@app.route(route="posts/{user_id}/{post_id}", methods=["GET"])
def post_history(req: func.HttpRequest) -> func.HttpResponse:
    user_id = req.route_params.get("user_id")
    post_id = req.route_params.get("post_id")

    try:
        if post_id:
            history = get_post_history_by_id(user_id, post_id)
            return func.HttpResponse(json.dumps({"history": history}), mimetype="application/json", status_code=200)
        else:
            posts = get_all_posts_by_user(user_id)
            return func.HttpResponse(json.dumps({"posts": posts}), mimetype="application/json", status_code=200)

    except Exception as e:
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500)

@app.route(route="posts/{user_id}", methods=["GET"])
def get_all_posts_by_user(req: func.HttpRequest):
    """
    Fetch all posts for a given user_id.
    """
    user_id = req.route_params.get("user_id")
    try:
        posts = get_all_posts_by_user(user_id)
        return posts
    except Exception as e:
        logging.error(f"Error fetching posts for user {user_id}: {e}")
        raise

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
    
@app.function_name(name="upload")
@app.route(route="upload", methods=["POST"])
async def upload_and_preprocess(req: func.HttpRequest) -> func.HttpResponse:
    try:
        formdata = await req.form()
        file = formdata.get("file")
        if not file:
            return func.HttpResponse(json.dumps({"error": "Missing file upload."}), status_code=400)

        temp_dir = tempfile.gettempdir()
        file_id = uuid.uuid4()
        temp_path = os.path.join(temp_dir, f"{file_id}-{file.filename}")

        with open(temp_path, "wb") as f:
            f.write(file.file.read())

        upload_file_to_blob("datasets", file.filename, temp_path)
        processed = os.path.join(temp_dir, f"processed-{file_id}.jsonl")
        preprocess_to_instruction_format(temp_path, processed)
        append_to_blob_batch(processed)

        return func.HttpResponse(json.dumps({"status": "success"}), status_code=200)

    except Exception as e:
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500)

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
    
@app.schedule(schedule="0 0 2 * * SUN", arg_name="mytimer", run_on_startup=False, use_monitor=True)
def finetune_trigger(mytimer: func.TimerRequest) -> None:
    logging.info("Scheduled job running...")
    logging.info("Timer triggered continuous fine-tune job")
    try:
        continuous_finetune()
        logging.info("Continuous fine-tune completed successfully.")
    except Exception as e:
        logging.error(f"Error in fine-tune job: {e}")

# Serve the OpenAPI JSON spec
@app.route(route="swagger.json", methods=["GET"])
def serve_openapi_spec(req: func.HttpRequest) -> func.HttpResponse:
    openapi_path = os.path.join(os.path.dirname(__file__), "openapi.json")
    with open(openapi_path, "r") as f:
        spec = json.load(f)
    return func.HttpResponse(json.dumps(spec), mimetype="application/json")

@app.route(route="docs", methods=["GET"])
def swagger_ui(req: func.HttpRequest) -> func.HttpResponse:
    swagger_path = os.path.join(os.path.dirname(__file__), "swagger_ui.html")
    with open(swagger_path, "r") as f:
        return func.HttpResponse(f.read(), mimetype="text/html")