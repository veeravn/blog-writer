from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient
from azure.ai.ml.entities import ManagedOnlineEndpoint, ManagedOnlineDeployment, CodeConfiguration, OnlineRequestSettings
from azure.core.exceptions import ResourceExistsError

from dotenv import load_dotenv
from config.env import ml_client, ENVIRONMENT_NAME, ENVIRONMENT_VERSION

load_dotenv()

def submit_mlendpoint_job():
    azureml_env = ml_client.environments.get(ENVIRONMENT_NAME, version=ENVIRONMENT_VERSION)

    # Create the online endpoint
    endpoint_name = "bloggen-mistral-endpoint"
    
    registered_model = ml_client.models.get(
        name="partha-style-mistral",
        version="24"
    )

    endpoint = ManagedOnlineEndpoint(
        name=endpoint_name,
        description="Blog generation endpoint using LoRA-tuned Mistral",
        auth_mode="key",  #
    )

    try:
        ml_client.online_endpoints.begin_create_or_update(endpoint).wait()
        print(f"✅ Created endpoint '{endpoint.name}'")
    except ResourceExistsError:
        print("ℹ️ Endpoint already exists. Proceeding with deployment update.")
    except Exception as e:
        print(f"❌ Failed to create or locate endpoint: {e}")
        raise

    # Create the deployment
    deployment_name = "mistral-deployment"
    deployment = ManagedOnlineDeployment(
        name=deployment_name,
        endpoint_name=endpoint_name,
        model=registered_model,
        environment=azureml_env,
        code_configuration=CodeConfiguration(
            code="./",                    # Path to folder with score.py and main.py
            scoring_script="score.py"     # Dummy script to satisfy Azure
        ),
        instance_type="Standard_E4s_v3",
        instance_count=1,
        request_settings=OnlineRequestSettings(
            request_timeout_ms=120000,
            max_concurrent_requests_per_instance=1
        )
    )

    print("Deployment args:", vars(deployment))
    print(f"🚀 Deploying model {registered_model.name} to endpoint '{endpoint_name}'...")
    ml_client.online_deployments.begin_create_or_update(deployment).wait()

    # Route all traffic to new deployment
    ml_client.online_endpoints.begin_update(
        endpoint_name=endpoint_name,
        traffic={deployment_name: 100}
    ).wait()

    print(f"✅ Model deployed to '{endpoint_name}' using deployment '{deployment_name}'")


if __name__ == "__main__":
    submit_mlendpoint_job()