import logging
import os
from dao.blob_storage import (
    download_blob,
    upload_to_blob,
    archive_and_clear_new_data
)
from .preprocess_data import preprocess_to_instruction_format
from .submit_train_job import submit_azureml_job
from utils.email_utils import send_email

PENDING_BLOB = "new_data.jsonl"
COMBINED_BLOB = "instruction_dataset.jsonl"
ARCHIVE_PREFIX = "archive/"
BATCH_SIZE = 10   # You can adjust this threshold

def continuous_finetune():
    logging.info("Continuous fine-tune started.")

    # Download new training data (if any)
    new_data_path = "/tmp/" + PENDING_BLOB
    combined_data_path = "/tmp/" + COMBINED_BLOB

    download_blob(PENDING_BLOB, new_data_path)
    download_blob(COMBINED_BLOB, combined_data_path)

    # Check if new data is sufficient to trigger fine-tuning
    with open(new_data_path, "r", encoding="utf-8") as f:
        new_lines = [line.strip() for line in f if line.strip()]
    if len(new_lines) < BATCH_SIZE:
        logging.info(f"Not enough new data ({len(new_lines)} < {BATCH_SIZE}), skipping fine-tune.")
        return

    # Merge new data into main dataset
    with open(combined_data_path, "a", encoding="utf-8") as f:
        for line in new_lines:
            f.write(line + "\n")
    upload_to_blob(combined_data_path, COMBINED_BLOB)

    # Preprocess data and launch training job
    preprocess_to_instruction_format(combined_data_path, combined_data_path)  # Overwrite as needed
    logging.info("Preprocessing completed. Submitting AzureML training job.")
    submit_azureml_job()
    logging.info("Fine-tune job completed.")

    # Archive the processed new_data
    archive_and_clear_new_data()

    # Send notification email (implement email_utils.send_email)
    send_email(
        subject="AI Blog Writer - Fine-tune Complete",
        message=f"Continuous fine-tune job completed and model is updating."
    )
    logging.info("Notification sent.")

    logging.info("Continuous fine-tune finished.")

if __name__ == "__main__":
    continuous_finetune()
