from dotenv import load_dotenv
import os

load_dotenv()
def get_env_variable(var_name: str, default_value: str = None) -> str:
    """Retrieve an environment variable with a default value."""
    return os.getenv(var_name, default_value)

AZURE_SUBSCRIPTION_ID="7cc0da73-46c1-4826-a73b-d7e49a39d6c1"
AZURE_RESOURCE_GROUP="rg-blog-gen"
AZURE_STORAGE_ACCOUNT="bloggensa"
AZURE_STORAGE_CONNECTION_STRING=os.getenv("AZURE_STORAGE_CONNECTION_STRING")
HF_TOKEN=os.getenv("HF_TOKEN")
BLOB_CONTAINER_NAME="bloggen"

COSMOS_ENDPOINT = os.getenv("COSMOS_DB_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOS_DB_KEY")
DATABASE_NAME = "AIWriterDB"
CONTAINER_NAME = "Posts"
MODEL_NAME = os.getenv("MODEL_NAME", "mistralai/Mistral-7B-v0.1")