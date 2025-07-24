# azure_functions_app/revise/__init__.py
import azure.functions as func
import json
from services.openai_client import revise_blog_post
from services.memory import get_user_tone_preferences
from services.cosmos_db import save_revision_log

async def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        original = req_body.get("original_prompt")
        initial_output = req_body.get("initial_output")
        feedback = req_body.get("feedback")
        user_id = req_body.get("user_id", "default_user")

        if not original or not feedback:
            return func.HttpResponse(
                json.dumps({"error": "Both 'original' and 'feedback' fields are required."}),
                status_code=400,
                mimetype="application/json"
            )

        preferences = get_user_tone_preferences(user_id)
        revised_post = revise_blog_post(initial_output, feedback, preferences)

        # Log the revision
        save_revision_log({
            "original_prompt": original,
            "initial_output": initial_output,
            "user_feedback": feedback,
            "final_output": revised_post,
            "user_id": user_id
        })

        return func.HttpResponse(
            json.dumps({"revised": revised_post}),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
