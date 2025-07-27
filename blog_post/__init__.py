import azure.functions as func
import json
import logging
from services.openai_client import generate_blog_post
from services.memory import get_preferences
from services.cosmos_db import get_post_by_id, save_post

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        data = req.get_json()
        prompt = data.get("prompt", "").strip()
        user_id = data.get("user_id")
        style_reference_post_id = data.get("style_reference_post_id")
        style_description = data.get("style_description")

        # 1. Style: reference post takes priority, else style_description, else None
        style_text = None
        if style_reference_post_id:
            ref_post = get_post_by_id(style_reference_post_id)
            if ref_post and "content" in ref_post:
                style_text = ref_post["content"]
        elif style_description:
            style_text = style_description

        # 2. Load preferences (optional, can be None)
        preferences = None
        if user_id:
            try:
                preferences = get_preferences(user_id)
            except Exception as e:
                logging.warning(f"Could not load preferences for {user_id}: {e}")

        # 3. Generate blog post (do not precompose prompt, style, or preferences)
        content = generate_blog_post(prompt=prompt, style=style_text, preferences=preferences)

        # 4. Save the post
        post_id = save_post(user_id=user_id, prompt=prompt, content=content)

        # 5. Return clean result
        return func.HttpResponse(
            json.dumps({"post_id": post_id, "content": content}),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logging.exception("Error in blog-post endpoint")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
