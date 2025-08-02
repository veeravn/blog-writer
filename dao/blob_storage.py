# services/blob_storage.pyimport json
from datetime import datetime, time
from azure.storage.blob import BlobServiceClient, ContentSettings
import config.env as env
import json

blob_service_client = BlobServiceClient.from_connection_string(env.AZURE_STORAGE_CONNECTION_STRING)
container_name = env.BLOB_CONTAINER_NAME
blog_container_client = blob_service_client.get_container_client("blogdata")
PREFERENCES_PREFIX = "preferences/"
BATCH_BLOB_NAME = "new_data.jsonl"


def upload_to_blob(container_name: str, blob_path: str, data: bytes, content_type: str = "application/octet-stream"):
    """
    Uploads raw bytes data to blob storage.
    """
    container_client = blob_service_client.get_container_client(container_name)
    container_client.upload_blob(
        name=blob_path,
        data=data,
        overwrite=True,
        content_settings=ContentSettings(content_type=content_type)
    )

def upload_file_to_blob(container_name: str, blob_path: str, file_path: str):
    """
    Uploads a file to blob storage.
    """
    with open(file_path, "rb") as file_data:
        upload_to_blob(container_name, blob_path, file_data.read(), content_type="application/octet-stream")

def list_blob_files(container_name):
    container_client = blob_service_client.get_container_client(container_name)
    return [blob.name for blob in container_client.list_blobs()]

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
    dataset_client = blob_service_client.get_container_client("datasets")
    dataset_client.delete_blob(filename)

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
        blob_client = blog_container_client.get_blob_client(blob_name)
        content = blob_client.download_blob().readall()
        return json.loads(content)
    except Exception:
        # Return empty preferences if not found or error occurs
        return {}

def save_preferences_to_blob(user_id: str, preferences: dict):
    blob_name = f"{PREFERENCES_PREFIX}{user_id}.json"
    blob_client = blog_container_client.get_blob_client(blob_name)
    blob_client.upload_blob(json.dumps(preferences), overwrite=True)

def append_to_blob_batch(preprocessed_file_path):
    # Download existing batch file (if any)
    container_client = blob_service_client.get_container_client(container_name)
    batch_blob = container_client.get_blob_client(BATCH_BLOB_NAME)
    batch_data = b""
    try:
        batch_data = batch_blob.download_blob().readall()
    except Exception:
        pass  # File may not exist yet

    # Read new data to append
    with open(preprocessed_file_path, "rb") as f:
        new_data = f.read()

    # Combine and upload
    combined = batch_data + new_data
    container_client.upload_blob(
        name=BATCH_BLOB_NAME,
        data=combined,
        overwrite=True,
        content_settings=ContentSettings(content_type="application/jsonl")
    )

def archive_and_clear_new_data(
    archive_dir: str = "processed"
):
    """
    Archives the processed new_data.jsonl and clears it for the next batch.
    """

    # Source blob (batch file)
    container_client = blob_service_client.get_container_client(container_name)
    batch_blob = container_client.get_blob_client(BATCH_BLOB_NAME)

    # Archive location with timestamp
    timestamp = datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M%S")
    archive_blob_name = f"{archive_dir}/new_data-{timestamp}.jsonl"
    archive_blob = container_client.get_blob_client(archive_blob_name)

    # Start copy (async, but we can check status if needed)
    copy = archive_blob.start_copy_from_url(batch_blob.url)
    print(f"Archiving {BATCH_BLOB_NAME} to {archive_blob_name} ...")
    
    # Wait for copy completion (optional, usually quick for small files)
    while archive_blob.get_blob_properties().copy.status == "pending":
        time.sleep(0.5)
    
    print("Archive complete. Clearing the batch file.")

    # Overwrite the source blob with empty content to clear it
    batch_blob.upload_blob(b"", overwrite=True)
    print("Batch file cleared and ready for next batch.")