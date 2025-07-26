import azure.functions as func
import json
import logging

from services.openai_client import generate_blog_post
from services.cosmos_db import save_post
from services.blob_storage import load_preferences_from_blob

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        data = req.get_json()
        prompt = data.get("prompt")
        style = data.get("style")
        user_id = data.get("user_id")

        if not prompt or not user_id:
            return func.HttpResponse("Missing required fields: 'prompt' and 'user_id'", status_code=400)

        # Load preferences from blob
        preferences = load_preferences_from_blob(user_id)

        # Generate blog post using preferences or style
        content = generate_blog_post(prompt=prompt, style=style, preferences=preferences)
        logging.info(f"Generated content for user {user_id}: {content}")

        # Save the post
        post_id = save_post(user_id=user_id, prompt=prompt, content=content)
        response_data = {"post_id": post_id, "content": content}
        return func.HttpResponse(
            json.dumps(response_data),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logging.exception("Failed to generate blog post")
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
