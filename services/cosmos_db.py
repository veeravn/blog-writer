import uuid
import logging
from azure.cosmos import CosmosClient, PartitionKey
from datetime import datetime
import config.env as env
from typing import List, Optional

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
        "timestamp": datetime.now().isoformat()
    }
    save_post(item)

def save_post(item: dict) -> str:
    """Save a post dict to Cosmos DB."""
    container.create_item(body=item)
    logger.info(f"Saved post {item['id']} for user {item.get('user_id')}")
    return item["id"]

def get_post_history(user_id: str, prompt: str) -> List[dict]:
    """Get all versions of a post by user_id and prompt (or post_id if you prefer)."""
    query = """
    SELECT * FROM c 
    WHERE c.user_id = @user_id AND c.prompt = @prompt
    ORDER BY c.version ASC
    """
    params = [
        {"name": "@user_id", "value": user_id},
        {"name": "@prompt", "value": prompt}
    ]
    return list(container.query_items(query=query, parameters=params, enable_cross_partition_query=True))

def get_post_by_id(post_id: str) -> Optional[dict]:
    """Get a single post by its unique id."""
    query = "SELECT * FROM c WHERE c.id=@id"
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