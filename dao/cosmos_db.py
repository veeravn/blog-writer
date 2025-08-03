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
        "timestamp": datetime.now(datetime.timezone.utc).isoformat()
    }
    save_post(item)

def save_post(item: dict) -> str:
    """Save a post dict to Cosmos DB."""
    container.create_item(body=item)
    logger.info(f"Saved post {item['id']} for user {item.get('user_id')}")
    return item["id"]

def get_all_posts_by_user(user_id: str):
    query = "SELECT * FROM c WHERE c.user_id = @user_id"
    params = [{"name": "@user_id", "value": user_id}]
    results = list(container.query_items(
        query=query, parameters=params, enable_cross_partition_query=True
    ))
    # Optionally sort or process results here
    return results

def get_post_history_by_id(user_id: str, post_id: str):
    query = (
        "SELECT * FROM c WHERE c.user_id = @user_id AND c.id = @post_id"
        " ORDER BY c.version ASC"
    )
    params = [
        {"name": "@user_id", "value": user_id},
        {"name": "@post_id", "value": post_id}
    ]
    results = list(container.query_items(
        query=query, parameters=params, enable_cross_partition_query=True
    ))
    return results

def get_post_by_id(post_id: str) -> Optional[dict]:
    """Get a single post by its unique id."""
    query = "SELECT * FROM c WHERE c.id=@id"
    params = [{"name": "@id", "value": post_id}]
    results = list(container.query_items(query=query, parameters=params, enable_cross_partition_query=True))
    return results[0] if results else None

def get_post_version_content(post_id: str, version: int) -> dict:
    """
    Fetches the post content for a specific post_id and version.
    """
    query = """
        SELECT * FROM Posts p 
        WHERE p.id = @post_id AND p.version = @version
    """
    params = [
        {"name": "@post_id", "value": post_id},
        {"name": "@version", "value": version},
    ]
    items = list(container.query_items(query=query, parameters=params, enable_cross_partition_query=True))
    return items[0] if items else None

def query_posts_by_ids(ids: List[str]) -> List[dict]:
    if not ids:
        return []
    # Use IN clause for batch lookup
    formatted_ids = ",".join(f"'{id}'" for id in ids)
    query = f"SELECT * FROM Posts p WHERE p.id IN ({formatted_ids})"
    return list(container.query_items(query=query, enable_cross_partition_query=True))

def get_new_training_examples(batch_size=50):
    query = f"SELECT * FROM Posts p WHERE NOT IS_DEFINED(p.used_for_finetune) OR p.used_for_finetune = false OFFSET 0 LIMIT {batch_size}"
    results = list(container.query_items(query=query, enable_cross_partition_query=True))
    return results

def mark_examples_as_processed(ids):
    for post_id in ids:
        items = list(container.query_items(
            query="SELECT * FROM Posts p WHERE p.id=@id",
            parameters=[{"name": "@id", "value": post_id}],
            enable_cross_partition_query=True
        ))
        if items:
            item = items[0]
            item["used_for_finetune"] = True
            container.replace_item(item=item["id"], body=item)