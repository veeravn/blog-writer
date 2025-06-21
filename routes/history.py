from fastapi import APIRouter, HTTPException
from services.cosmos_db import get_post_history

router = APIRouter()

@router.get("/{post_id}")
def get_history(post_id: str):
    try:
        return get_post_history(post_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
