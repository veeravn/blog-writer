import shutil
from tempfile import NamedTemporaryFile
from azure.storage.blob import BlobServiceClient
import config.env as env

blob_service_client = BlobServiceClient.from_connection_string(env.AZURE_STORAGE_CONNECTION_STRING)
container_name = env.BLOB_CONTAINER_NAME
container_client = blob_service_client.get_container_client("blogdata")

def save_to_temp(file):
    with NamedTemporaryFile(delete=False, suffix=file.filename) as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        return temp_file.name

def upload_file(path: str, filename: str):
    with open(path, "rb") as file:
        container_client.upload_blob(filename, file.read(), overwrite=True)

def delete_dataset(filename):
    container_client.delete_blob(filename)

