#scripts/submit_train_job.py
from azure.ai.ml import command, Input, Output
from azure.ai.ml.entities import Model
from azure.ai.ml.constants import AssetTypes

from dotenv import load_dotenv
import config.env as env

load_dotenv()

if not env.HF_TOKEN:
    raise ValueError("HF_TOKEN environment variable is not set. Please set it to your Hugging Face token.")

def submit_azureml_job():

    azureml_env = env.ml_client.environments.get(env.ENVIRONMENT_NAME, version=env.ENVIRONMENT_VERSION)

    # Create the training job
    job = command(
        code="./scripts",  # directory with train_lora.py
        command=env.TRAINING_COMMAND,
        environment=azureml_env,
        inputs={
            "dataset": Input(
                path=env.INSTRUCTION_DATASET_URI,
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

    model_output_path = f"azureml://jobs/{completed_job.name}/outputs/model_output"
    registered_model = env.ml_client.models.create_or_update(
        Model(
            name="partha-style-mistral",
            path=model_output_path,
            type="custom_model",
            description="LoRA fine-tuned Mistral-7B on Partha Naidu's writing style"
        )
    )

    print(f"✅ Model registered: {registered_model.name} (v{registered_model.version})")

if __name__ == "__main__":
    submit_azureml_job()