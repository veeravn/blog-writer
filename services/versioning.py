import uuid
from datetime import datetime
from .cosmos_db import save_post

def create_versioned_post(prompt, content):
    return {
        "id": str(uuid.uuid4()),
        "prompt": prompt,
        "content": content,
        "timestamp": datetime.utcnow().isoformat()
    }

def update_post_with_feedback(original, feedback, revision):
    new_version = create_versioned_post(original["prompt"], revision)
    new_version["feedback"] = feedback
    new_version["parent_id"] = original["id"]
    return new_version


def log_revision(data):
    save_post({
        "user_id": data["user_id"],
        "prompt": data["prompt"],
        "initial_draft": data["initial_draft"],
        "feedback": data["feedback"],
        "revised_draft": data["revised_draft"],
        "type": "revision"
    })
