from services.blob_storage import archive_and_clear_new_data
from .preprocess_data import preprocess_to_instruction_format
from .submit_train_job import submit_azureml_job

RAW_DATA_FILE = "data/new_feedback.jsonl"
PROCESSED_FILE = "data/preprocessed.jsonl"
FINE_TUNE_THRESHOLD = 20  # Adjust as needed

def count_lines(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return sum(1 for _ in f if f.strip())

def should_fine_tune():
    return count_lines(RAW_DATA_FILE) >= FINE_TUNE_THRESHOLD

def continuous_finetune():
    if not should_fine_tune():
        print("Not enough new feedback to trigger fine-tuning.")
        return

    print("Preprocessing new feedback for fine-tuning...")
    preprocess_to_instruction_format(RAW_DATA_FILE, PROCESSED_FILE)

    print("Submitting Azure ML fine-tuning job...")
    # submit_azureml_job should pick up the correct dataset path if configured to do so,
    # or modify it to accept a file argument if needed
    success = submit_azureml_job()

    if success:
        archive_and_clear_new_data()
    else:
        print("Fine-tune failed. Not archiving or clearing batch file.")

if __name__ == "__main__":
    continuous_finetune()
