from azure.storage.blob import BlobServiceClient
import os

blob_service_client = BlobServiceClient.from_connection_string(os.getenv("AZURE_STORAGE_CONNECTION_STRING"))
container_name = os.getenv("BLOB_CONTAINER_NAME", "bloggen")
container_client = blob_service_client.get_container_client("blogdata")

def save_to_temp(file):
    with NamedTemporaryFile(delete=False, suffix=file.filename) as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        return temp_file.name

def upload_file(path: str, filename: str):
    with open(path, "rb") as file:
        upload_blob(filename, file.read())

def delete_dataset(filename):
    container_client.delete_blob(filename)

