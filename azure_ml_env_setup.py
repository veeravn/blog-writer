# azure_ml_env_setup.py
# This script sets up or updates a custom Azure ML environment for training a LoRA model using Mistral-7B.

from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient
from azure.ai.ml.entities import Environment

# Azure ML workspace details
SUBSCRIPTION_ID = "7cc0da73-46c1-4826-a73b-d7e49a39d6c1"
RESOURCE_GROUP = "rg-blog-gen"
WORKSPACE_NAME = "bloggen-ml"
ENVIRONMENT_NAME = "mistral-env"

# Custom ACR image for your environment
ACR_IMAGE = "bloggencr.azurecr.io/blog-gen:latest"

def create_or_update_environment():
    # Authenticate with Azure ML
    ml_client = MLClient(
        DefaultAzureCredential(),
        subscription_id=SUBSCRIPTION_ID,
        resource_group_name=RESOURCE_GROUP,
        workspace_name=WORKSPACE_NAME,
    )

    # Define the environment
    mistral_env = Environment(
        name=ENVIRONMENT_NAME,
        description="Custom blog-gen LoRA training env with bitsandbytes, transformers, etc.",
        image=ACR_IMAGE,
        conda_file="conda_env.yml"
    )

    # Register it
    registered_env = ml_client.environments.create_or_update(mistral_env)
    print(f"✅ Registered environment: {registered_env.name}")

if __name__ == "__main__":
    create_or_update_environment()
