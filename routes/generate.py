from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from services.openai_client import generate_blog_post
from services.memory import store_prompt_context, get_preferences
from services.cosmos_db import save_post
from models.blog_post import BlogPost
from uuid import uuid4

router = APIRouter()

class GenerateRequest(BaseModel):
    prompt: str
    style: str = None

@router.post("/")
def generate_blog_post_route(request: GenerateRequest):
    try:
        user_id = str(uuid4())  # placeholder until auth
        preferences = get_preferences(user_id)
        output = generate_blog_post(request.prompt, request.style, preferences)
        save_post(request.prompt, output, version=1)
        return {"output": output}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/new-post")
async def new_post(request: Request, blog: BlogPost):
    user_id = request.headers.get("X-User-ID", str(uuid4()))
    preferences = get_preferences(user_id)
    content = generate_blog_post(blog.prompt, blog.style, preferences)
    store_prompt_context(user_id, blog.prompt, blog.style or "default")
    save_post(blog.prompt, content, version=1)
    return {"generated_post": content, "status": "draft"}
