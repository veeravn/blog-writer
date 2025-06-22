from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient
import os

load_dotenv()
def get_env_variable(var_name: str, default_value: str = None) -> str:
    """Retrieve an environment variable with a default value."""
    return os.getenv(var_name, default_value)

AZURE_SUBSCRIPTION_ID="7cc0da73-46c1-4826-a73b-d7e49a39d6c1"
AZURE_RESOURCE_GROUP="rg-blog-gen"
AZURE_STORAGE_ACCOUNT="bloggensa"
AZURE_STORAGE_CONNECTION_STRING=get_env_variable("AZURE_STORAGE_CONNECTION_STRING")
HF_TOKEN=get_env_variable("HF_TOKEN")
BLOB_CONTAINER_NAME="bloggen"

COSMOS_CONNECTION_STRING = get_env_variable("COSMOS_CONNECTION_STRING")
DATABASE_NAME = "AIWriterDB"
CONTAINER_NAME = "Posts"
MODEL_NAME = get_env_variable("MODEL_NAME", "mistralai/Mistral-7B-v0.1")

if not COSMOS_CONNECTION_STRING:
    raise ValueError("Missing Cosmos DB credentials in environment variables.")
if not AZURE_STORAGE_CONNECTION_STRING:
    raise ValueError("Missing Azure Storage credentials in environment variables.")
if not HF_TOKEN:
    raise ValueError("Missing Hugging Face token in environment variables.")

WORKSPACE_NAME = "bloggen-ml"
COMPUTE_CLUSTER = "bloggen-compute"
ENVIRONMENT_NAME = "mistral-env"
ENVIRONMENT_VERSION = "13"

ml_client = MLClient(
    credential=DefaultAzureCredential(),
    subscription_id=AZURE_SUBSCRIPTION_ID,
    resource_group_name=AZURE_RESOURCE_GROUP,
    workspace_name=WORKSPACE_NAME
)