from datetime import datetime
from uuid import uuid4
from typing import Optional, List
from dao.cosmos_db import get_post_by_id, save_post, query_posts_by_ids, get_post_history

def create_post_version(
    user_id: str,
    prompt: str,
    content: str,
    feedback: Optional[str] = None,
    tone: Optional[str] = None,
    version: int = 1,
    related_versions: Optional[List[str]] = None
) -> dict:
    """Create and save a new version of a post."""
    new_post = {
        "id": str(uuid4()),
        "user_id": user_id,
        "prompt": prompt,
        "content": content,
        "tone": tone,
        "version": version,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": None,
        "feedback": feedback,
        "related_versions": related_versions or []
    }
    save_post(new_post)
    return new_post

def revise_post_version(post_id: str, new_content: str, feedback: str) -> dict:
    """Revise a post and save as new version."""
    original = get_post_by_id(post_id)
    if not original:
        raise ValueError("Original post/version not found.")

    new_post = {
        "id": str(uuid4()),
        "user_id": original["user_id"],
        "prompt": original["prompt"],
        "content": new_content,
        "tone": original.get("tone"),
        "version": original["version"] + 1,
        "created_at": original["created_at"],
        "updated_at": datetime.utcnow().isoformat(),
        "feedback": feedback,
        "related_versions": [post_id] + original.get("related_versions", [])
    }
    save_post(new_post)
    return new_post

def get_all_versions(post_id: str) -> List[dict]:
    """Return the current post and all its related versions, sorted by version."""
    current_post = get_post_by_id(post_id)
    if not current_post:
        raise ValueError(f"No post found with id: {post_id}")

    related_ids = current_post.get("related_versions", [])
    all_versions = [current_post]
    if related_ids:
        related_posts = query_posts_by_ids(related_ids)
        all_versions += related_posts

    # Sort by version ascending
    return sorted(all_versions, key=lambda post: post.get("version", 0))

def revert_to_post_version(user_id: str, target_post_id: str) -> dict:
    """Create a new version from a previous version."""
    old_post = get_post_by_id(target_post_id)
    if not old_post:
        raise ValueError("Target version not found.")

    new_post = create_post_version(
        user_id=user_id,
        prompt=old_post['prompt'],
        content=old_post['content'],
        tone=old_post.get("tone"),
        version=old_post.get("version", 1) + 1,
        related_versions=[target_post_id] + old_post.get("related_versions", [])
    )
    return {
        "post_id": new_post["id"],
        "content": old_post["content"],
        "message": "Reverted to previous version successfully."
    }

def compare_post_versions(post_id1: str, post_id2: str) -> dict:
    """Return both versions for comparison (side-by-side)."""
    post1 = get_post_by_id(post_id1)
    post2 = get_post_by_id(post_id2)
    if not post1 or not post2:
        raise ValueError("One or both posts not found for comparison.")
    return {
        "version_1": post1,
        "version_2": post2
    }
