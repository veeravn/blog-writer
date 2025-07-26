# services/versioning.py

from datetime import datetime
from typing import Optional, List
from uuid import uuid4
from services.cosmos_db import get_post_by_id, query_posts_by_ids

def create_post_version(prompt: str, content: str, feedback: Optional[str] = None) -> dict:
    return {
        "id": str(uuid4()),
        "prompt": prompt,
        "content": content,
        "version": 1,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": None,
        "feedback": feedback,
        "related_versions": []
    }

def revise_post_version(original_post: dict, new_content: str, feedback: str) -> dict:
    return {
        "id": str(uuid4()),
        "prompt": original_post["prompt"],
        "content": new_content,
        "version": original_post["version"] + 1,
        "created_at": original_post["created_at"],
        "updated_at": datetime.utcnow().isoformat(),
        "feedback": feedback,
        "related_versions": [original_post["id"]] + original_post.get("related_versions", [])
    }

def get_all_versions(post_id: str) -> List[dict]:
    """
    Given a post ID, returns the current post and all its related versions.
    Assumes post documents have a `related_versions` field storing ancestor version IDs.
    """
    current_post = get_post_by_id(post_id)
    if not current_post:
        raise ValueError(f"No post found with id: {post_id}")

    # Fetch all related version IDs (excluding self)
    related_ids = current_post.get("related_versions", [])
    
    if not related_ids:
        return [current_post]

    # Fetch all related version documents
    related_posts = query_posts_by_ids(related_ids)

    # Sort by version number (ascending)
    all_versions = related_posts + [current_post]
    return sorted(all_versions, key=lambda post: post.get("version", 0))
