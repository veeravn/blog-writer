import json
import config.env as env
import os
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

REVISION_LOG_PATH = "data/revision_logs.json"
OUTPUT_JSONL_PATH = "data/new_finetune_data.jsonl"

BLOB_CONTAINER = "bloggen-data"
BLOB_PATH = "finetune/new_data.jsonl"

def load_revision_logs():
    if not os.path.exists(REVISION_LOG_PATH):
        print(f"No revision log found at {REVISION_LOG_PATH}")
        return []
    with open(REVISION_LOG_PATH, "r") as f:
        return json.load(f)

def convert_to_instruction_format(logs):
    messages = []
    for entry in logs:
        system_prompt = (
            f"Original Prompt: {entry['original_prompt']}\n"
            f"User Feedback: {entry['user_feedback']}"
        )
        assistant_output = entry["final_output"]
        messages.append({
            "messages": [
                {"role": "user", "content": system_prompt},
                {"role": "assistant", "content": assistant_output}
            ]
        })
    return messages


def save_jsonl(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        for example in data:
            f.write(json.dumps(example) + "\n")
    print(f"Saved new fine-tune dataset to {path}")

def upload_to_blob(local_path, container_name, blob_path):
    connection_string = env.AZURE_STORAGE_CONNECTION_STRING
    if not connection_string:
        raise ValueError("Missing AZURE_STORAGE_CONNECTION_STRING in .env")

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_path)

    with open(local_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    print(f"Uploaded {local_path} to blob storage at {container_name}/{blob_path}")

def main():
    logs = load_revision_logs()
    if not logs:
        print("No logs to process.")
        return

    formatted = convert_to_instruction_format(logs)
    save_jsonl(formatted, OUTPUT_JSONL_PATH)
    upload_to_blob(OUTPUT_JSONL_PATH, BLOB_CONTAINER, BLOB_PATH)

if __name__ == "__main__":
    main()
