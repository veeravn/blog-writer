import os
import uuid
import logging
from azure.cosmos import CosmosClient, PartitionKey
from datetime import datetime
from dotenv import load_dotenv
import config.env as env

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


client = CosmosClient.from_connection_string(env.COSMOS_CONNECTION_STRING)
database = client.create_database_if_not_exists(id=env.DATABASE_NAME)
container = database.create_container_if_not_exists(
    id=env.CONTAINER_NAME,
    partition_key=PartitionKey(path="/user_id")
)

def save_post(user_id: str, prompt: str, content: str, tone: str = None, version: int = 1):
    post_id = str(uuid.uuid4())
    item = {
        "id": post_id,
        "user_id": user_id,
        "prompt": prompt,
        "content": content,
        "tone": tone,
        "version": version,
        "timestamp": datetime.utcnow().isoformat()
    }

    container.create_item(body=item)
    logger.info(f"Saved post {post_id} for user {user_id}")
    return post_id

def get_post_history(user_id: str, post_id: str):
    query = """
    SELECT * FROM c 
    WHERE c.user_id = @user_id AND c.post_id = @post_id
    ORDER BY c.version ASC
    """
    params = [
        {"name": "@user_id", "value": user_id},
        {"name": "@post_id", "value": post_id}
    ]

def get_post_versions(user_id: str, prompt: str):
    query = "SELECT * FROM Posts p WHERE p.user_id=@user_id AND p.prompt=@prompt ORDER BY p.timestamp DESC"
    params = [
        {"name": "@user_id", "value": user_id},
        {"name": "@prompt", "value": prompt}
    ]
    items = list(container.query_items(query=query, parameters=params, enable_cross_partition_query=True))
    return items

def save_tone_preference(user_id: str, tone: str):
    preference_id = f"tone_pref_{user_id}"
    item = {
        "id": preference_id,
        "user_id": user_id,
        "type": "tone_preference",
        "tone": tone,
        "updated": datetime.utcnow().isoformat()
    }
    container.upsert_item(item)
    logger.info(f"Updated tone preference for user {user_id}")

def get_tone_preference(user_id: str) -> str:
    try:
        item = container.read_item(item=f"tone_pref_{user_id}", partition_key=user_id)
        return item.get("tone", "neutral")
    except Exception as e:
        logger.warning(f"No tone preference found for user {user_id}: {e}")
        return "neutral"
def save_revision_log(log_data: dict):
    container = client.get_container_client(env.CONTAINER_NAME)
    log_data["id"] = str(uuid.uuid4())  # Ensure unique ID
    log_data["type"] = "revision_log"
    log_data["timestamp"] = datetime.now(datetime.timezone.utc).isoformat()
    container.create_item(log_data)

def fetch_user_preferences(container, user_id: str) -> dict:
    query = "SELECT TOP 1 * FROM c WHERE c.user_id=@user_id AND c.type='preferences' ORDER BY c.timestamp DESC"
    items = list(container.query_items(
        query=query,
        parameters=[{"name": "@user_id", "value": user_id}],
        enable_cross_partition_query=True
    ))
    return items[0].get("preferences", {}) if items else {}

def save_prompt_history(container, user_id: str, prompt: str, response: str, metadata: dict = None):
    item = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "type": "prompt_history",
        "prompt": prompt,
        "response": response,
        "metadata": metadata or {},
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
    container.upsert_item(item)