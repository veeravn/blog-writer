from azure.ai.ml.entities import ManagedOnlineEndpoint, ManagedOnlineDeployment, CodeConfiguration, OnlineRequestSettings
from azure.core.exceptions import ResourceExistsError

from dotenv import load_dotenv
from config.env import ml_client, ENVIRONMENT_NAME, ENVIRONMENT_VERSION, MODEL_VERSION, FT_MODEL_NAME
from scripts.secrets_loader import get_env_vars

load_dotenv()

def submit_mlendpoint_job():
    azureml_env = ml_client.environments.get(ENVIRONMENT_NAME, version=ENVIRONMENT_VERSION)

    # Create the online endpoint
    endpoint_name = "partha-style-endpoint"

    registered_model = ml_client.models.get(
        name=FT_MODEL_NAME,
        version=MODEL_VERSION  # Ensure this matches the version you registered
    )

    # Create the deployment
    deployment_name = FT_MODEL_NAME
    env_vars = get_env_vars(
        vault_name="bloggenml4401779802",
        secret_names=[
            "COSMOS-CONNECTION-STRING",
            "AZURE-STORAGE-CONNECTION-STRING",
            "BLOB-CONTAINER-NAME",
            "AZURE-RESOURCE-GROUP",
            "AZURE-STORAGE-ACCOUNT",
            "AZURE-SUBSCRIPTION-ID",
            "CONTAINER-NAME",
            "DATABASE-NAME",
            "HF-TOKEN",
            "MODEL-NAME"
        ]
    )
    
    deployment = ManagedOnlineDeployment(
        name=deployment_name,
        endpoint_name=endpoint_name,
        model=registered_model,
        environment=azureml_env,
        environment_variables=env_vars,
        code_configuration=CodeConfiguration(
            code="./",   # or "./" if main.py is in root
            scoring_script="score.py"
        ),
        instance_type="Standard_NC6s_v3",
        instance_count=1,
        # environment_variables=env_vars,
        request_settings=OnlineRequestSettings(
            request_timeout_ms=120000,
            max_concurrent_requests_per_instance=1
        ),
    )

    print("Deployment args:", vars(deployment))
    print(f"🚀 Deploying model {registered_model.name} to endpoint '{endpoint_name}'...")
    ml_client.online_deployments.begin_create_or_update(deployment).wait()

    endpoint = ManagedOnlineEndpoint(
        name=endpoint_name,
        description="Blog Writer model endpoint using LoRA-tuned Mistral",
        auth_mode="key",
        tags={"project": "blog-writer"},
        traffic={"blue": 100}
    )
    # Route all traffic to new deployment
    ml_client.online_endpoints.begin_create_or_update(
        endpoint=endpoint
    ).wait()

    print(f"✅ Model deployed to '{endpoint_name}' using deployment '{deployment_name}'")


if __name__ == "__main__":
    submit_mlendpoint_job()