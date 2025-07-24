import azure.functions as func
import json, logging, uuid
from datetime import datetime

from services.openai_client import generate_blog_post
from services.memory import store_prompt_context, get_user_tone_preferences
from services.cosmos_db import save_post

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.function_name(name="blog_post_handler")
@app.route(route="blog-post", methods=["POST"])
def blog_post_handler(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()

        user_id = body.get("user_id")
        prompt = body.get("prompt")
        style = body.get("style")
        preferences = body.get("preferences")
        save = body.get("save", False)

        # Generate blog post using OpenAI client
        content = generate_blog_post(prompt, style=style, preferences=preferences)

        if save:
            version = 1
            post_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat()

            post_record = {
                "id": post_id,
                "user_id": user_id,
                "prompt": prompt,
                "content": content,
                "version": version,
                "timestamp": timestamp
            }

            save_post(post_record)
            store_prompt_context(user_id, prompt, preferences or {})

            return func.HttpResponse(json.dumps(post_record), mimetype="application/json", status_code=201)

        # Just return generated content without saving
        return func.HttpResponse(json.dumps({"content": content}), mimetype="application/json", status_code=200)

    except Exception as e:
        logging.exception("Error in blog_post_handler")
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
