from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from services.openai_client import revise_blog_post
from services.memory import get_user_tone_preferences
from services.cosmos_db import save_revision_log

router = APIRouter()

class RevisionRequest(BaseModel):
    original_prompt: str
    initial_output: str
    feedback: str

@router.post("/revise")
async def revise_post(request: Request, data: RevisionRequest):
    try:
        user_id = request.headers.get("X-User-ID", "anonymous")
        preferences = get_user_tone_preferences(user_id)
        revised_post = revise_blog_post(data.initial_output, data.feedback, preferences)
        save_revision_log({
            "original_prompt": data.original_prompt,
            "initial_output": data.initial_output,
            "user_feedback": data.feedback,
            "final_output": revised_post,
            "user_id": user_id
        })
        return {"revised_post": revised_post}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
