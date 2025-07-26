# services/blob_storage.pyimport json
from azure.storage.blob import BlobServiceClient, ContentSettings
import config.env as env
import json

blob_service_client = BlobServiceClient.from_connection_string(env.AZURE_STORAGE_CONNECTION_STRING)
container_name = env.BLOB_CONTAINER_NAME
container_client = blob_service_client.get_container_client("blogdata")
PREFERENCES_PREFIX = "preferences/"


def upload_to_blob(container_name: str, blob_path: str, data: bytes, content_type: str = "application/octet-stream"):
    """
    Uploads raw bytes data to blob storage.
    """
    container_client.upload_blob(
        name=blob_path,
        data=data,
        overwrite=True,
        content_settings=ContentSettings(content_type=content_type)
    )


def download_blob(container_name: str, blob_path: str) -> bytes:
    """
    Downloads raw bytes from blob storage.
    """
    blob = blob_service_client.get_blob_client(container_name, blob_path)
    return blob.download_blob().readall()


def delete_dataset(filename: str):
    """
    Deletes a dataset blob from the 'datasets' container.
    """
    blob_service_client.delete_blob("datasets", filename)


def save_json_to_blob(container_name: str, blob_path: str, obj: dict):
    """
    Saves a JSON-serializable object to blob storage.
    """
    json_bytes = json.dumps(obj, indent=2).encode("utf-8")
    upload_to_blob(container_name, blob_path, json_bytes, content_type="application/json")


def load_json_from_blob(container_name: str, blob_path: str) -> dict:
    """
    Loads and parses a JSON blob. Returns an empty dict if the blob is missing.
    """
    try:
        blob_bytes = download_blob(container_name, blob_path)
        return json.loads(blob_bytes.decode("utf-8"))
    except Exception:
        return {}

def load_preferences_from_blob(user_id: str) -> dict:
    blob_name = f"{PREFERENCES_PREFIX}{user_id}.json"
    try:
        blob_client = container_client.get_blob_client(blob_name)
        content = blob_client.download_blob().readall()
        return json.loads(content)
    except Exception:
        # Return empty preferences if not found or error occurs
        return {}


def save_preferences_to_blob(user_id: str, preferences: dict):
    blob_name = f"{PREFERENCES_PREFIX}{user_id}.json"
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(json.dumps(preferences), overwrite=True)