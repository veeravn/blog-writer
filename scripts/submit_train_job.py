
from azure.ai.ml.entities import Environment
from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient, command, Input, Output
from azure.ai.ml.entities import Model, ManagedOnlineEndpoint, ManagedOnlineDeployment, CodeConfiguration
from azure.ai.ml.constants import AssetTypes
from azure.core.exceptions import ResourceExistsError

import os
from dotenv import load_dotenv

load_dotenv()

hf_token = os.getenv("HF_TOKEN")
if not hf_token:
    raise ValueError("HF_TOKEN environment variable is not set. Please set it to your Hugging Face token.")

subscription_id = "7cc0da73-46c1-4826-a73b-d7e49a39d6c1"
resource_group = "rg-blog-gen"
workspace_name = "bloggen-ml"
compute_cluster = "bloggen-compute"
environment_name = "mistral-env"

ml_client = MLClient(
    credential=DefaultAzureCredential(),
    subscription_id=subscription_id,
    resource_group_name=resource_group,
    workspace_name=workspace_name
)

def submit_azureml_job():
    
    # Create the training job
    job = command(
        code="./scripts",  # directory with train_lora.py
        command="python train_lora.py --dataset ${{inputs.dataset}} --output_dir ${{outputs.model_output}}",
        environment=f"{environment_name}:12",
        inputs={
            "dataset": Input(
                path="azureml://subscriptions/7cc0da73-46c1-4826-a73b-d7e49a39d6c1/resourcegroups/rg-blog-gen/workspaces/bloggen-ml/datastores/workspaceblobstore/paths/instruction_dataset.jsonl",
                type=AssetTypes.URI_FILE,
            )
        },
        outputs={
            "model_output": Output(type=AssetTypes.URI_FOLDER, mode="rw_mount")
        },
        compute=compute_cluster,
        display_name="train-mistral-lora",
        experiment_name="bloggen-mistral-finetune",
        environment_variables={"HF_TOKEN": hf_token}
    )

    job = ml_client.jobs.create_or_update(job)
    print("✅ Azure ML training job submitted.")
    ml_client.jobs.stream(job.name)

    completed_job = ml_client.jobs.get("ashy_room_wp5lw6wxz4")
    model_output_path = f"azureml://jobs/{completed_job.name}/outputs/model_output"
    registered_model = ml_client.models.get(
        Model(
            name="partha-style-mistral",
            path=model_output_path,
            type="custom_model",
            description="LoRA fine-tuned Mistral-7B on Partha Naidu's writing style"
        )
    )

    print(f"✅ Model registered: {registered_model.name} (v{registered_model.version})")

    # Deploy to online endpoint
    endpoint_name = "mistral-blog-endpoint"
    deployment_name = f"{registered_model.name}-{registered_model.version}"

    endpoint = ManagedOnlineEndpoint(
        name=endpoint_name,
        description="Blog generation endpoint using LoRA-tuned Mistral",
        auth_mode="key",  #
    )

    try:
        ml_client.online_endpoints.begin_create_or_update(endpoint)
        print(f"✅ Created endpoint '{endpoint.name}'")
    except ResourceExistsError:
        print("ℹ️ Endpoint already exists. Proceeding with deployment update.")
    except Exception as e:
        print(f"❌ Failed to create or locate endpoint: {e}")
        raise
    environment_variables = {
        "AZUREML_ENTRY_SCRIPT": "score.py"
    }
    
    deployment = ManagedOnlineDeployment(
        name=deployment_name,
        endpoint_name=endpoint_name,
        model=registered_model.id,
        instance_type="Standard_NC6s_v3",
        instance_count=1,
        code_configuration=CodeConfiguration(
            code="./scripts/inference",  # Folder with score.py
            scoring_script="score.py"
        ),
        environment=f"{environment_name}:12",  # Reuse or set to match env.yaml
        environment_variables=environment_variables
    )

    print(f"🚀 Deploying model {registered_model.name} to endpoint '{endpoint_name}'...")
    ml_client.online_deployments.begin_create_or_update(deployment).wait()

    # Route all traffic to new deployment
    ml_client.online_endpoints.begin_update(
        endpoint_name=endpoint_name,
        traffic={deployment_name: 100}
    ).wait()

    print(f"✅ Model deployed to '{endpoint_name}' using deployment '{deployment_name}'")


if __name__ == "__main__":
    submit_azureml_job()