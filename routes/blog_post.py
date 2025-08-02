# routes/generate.py
import azure.functions as func
import json
import logging
from function_app import app
from services.openai_client import generate_blog_post
from services.memory import get_preferences
from dao.cosmos_db import get_post_by_id
from services.versioning import create_post_version

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
