import logging
from services.continuous_finetune import continuous_finetune

def main(mytimer: dict) -> None:
    logging.info("Timer triggered continuous fine-tune job")
    try:
        continuous_finetune()
        logging.info("Continuous fine-tune completed successfully.")
    except Exception as e:
        logging.error(f"Error in fine-tune job: {e}")
