#scripts/submit_train_job.py
from azure.ai.ml import command, Input, Output
from azure.ai.ml.entities import Model
from azure.ai.ml.constants import AssetTypes

import config.env as env

if not env.HF_TOKEN:
    raise ValueError("HF_TOKEN environment variable is not set. Please set it to your Hugging Face token.")

def submit_azureml_job(dataset_path) -> bool:
    try:
        azureml_env = env.ml_client.environments.get(env.ENVIRONMENT_NAME, version=env.ENVIRONMENT_VERSION)

        # Create the training job
        job = command(
            code="./scripts",  # directory with train_lora.py
            command=env.TRAINING_COMMAND,
            environment=azureml_env,
            inputs={
                "dataset": Input(
                    path=dataset_path,
                    type=AssetTypes.URI_FILE,
                )
            },
            outputs={
                "model_output": Output(type=AssetTypes.URI_FOLDER, mode="rw_mount")
            },
            compute=env.COMPUTE_CLUSTER,
            display_name="train-mistral-lora",
            experiment_name="bloggen-mistral-finetune",
            environment_variables={"HF_TOKEN": env.HF_TOKEN}
        )
        completed_job = env.ml_client.jobs.create_or_update(job)
        print("✅ Azure ML training job submitted.")
        env.ml_client.jobs.stream(completed_job.name)

        model_output_path = f"azureml://jobs/{completed_job.name}/outputs/model_output/merged_model"
        registered_model = env.ml_client.models.create_or_update(
            Model(
                name=env.FT_MODEL_NAME,
                path=model_output_path,
                type="custom_model",
                description="Merged Mistral-7B fine-tuned on Partha Naidu's writing style (LoRA + base)",
            )
        )

        print(f"✅ Model registered: {registered_model.name} (v{registered_model.version})")

        return True
    except Exception as e:
        print(f"❌ Error submitting Azure ML job: {e}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        dataset_path = sys.argv[1]
    else:
        dataset_path = env.INSTRUCTION_DATASET_URI
    submit_azureml_job(dataset_path)