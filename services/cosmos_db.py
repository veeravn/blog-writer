import uuid
import logging
from azure.cosmos import CosmosClient, PartitionKey
from datetime import datetime
import config.env as env
from typing import List

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

def get_post_by_id(post_id: str) -> dict:
    query = "SELECT * FROM Posts p WHERE p.id=@id"
    params = [{"name": "@id", "value": post_id}]
    results = list(container.query_items(query=query, parameters=params, enable_cross_partition_query=True))
    return results[0] if results else None

def query_posts_by_ids(ids: List[str]) -> List[dict]:
    if not ids:
        return []
    # Use IN clause for batch lookup
    formatted_ids = ",".join(f"'{id}'" for id in ids)
    query = f"SELECT * FROM Posts p WHERE p.id IN ({formatted_ids})"
    return list(container.query_items(query=query, enable_cross_partition_query=True))