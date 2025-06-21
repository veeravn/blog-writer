import os, argparse
import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    Trainer,
    TrainingArguments,
    DataCollatorForSeq2Seq,
)
from transformers.trainer_utils import get_last_checkpoint
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from huggingface_hub import login

try:
    import bitsandbytes as bnb
    print("✅ bitsandbytes is installed:", bnb.__version__)
except Exception as e:
    print("❌ bitsandbytes not installed properly:", e)

parser = argparse.ArgumentParser()
parser.add_argument("--dataset", type=str, required=True)
parser.add_argument("--output_dir", type=str, required=True)
args = parser.parse_args()

MODEL_NAME = "mistralai/Mistral-7B-v0.1"
DATA_PATH = args.dataset
OUTPUT_DIR = args.output_dir

os.makedirs(OUTPUT_DIR, exist_ok=True)
hf_token = os.environ.get("HF_TOKEN")
if hf_token:
    login(hf_token)


def format_prompt(example):
    """
    Flatten the messages field into a prompt-completion style string.
    Example:
        User: Write a LinkedIn post...
        Assistant: Use Log Analytics...
    """
    messages = example["messages"]
    text = ""
    for message in messages:
        role = message["role"].capitalize()
        content = message["content"]
        text += f"{role}: {content}\n"
    return {"text": text}

def main():
    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True, use_fast=False)
    tokenizer.pad_token = tokenizer.eos_token  # For compatibility

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        device_map="auto",
        trust_remote_code=True,
        torch_dtype=torch.bfloat16,
    )

    # Prepare model for LoRA if needed
    model = prepare_model_for_kbit_training(model)
    peft_config = LoraConfig(
        r=8,
        lora_alpha=16,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        lora_dropout=0.1,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, peft_config)

    # Load and preprocess dataset
    dataset = load_dataset("json", data_files=DATA_PATH, split="train")
    dataset = dataset.map(format_prompt)

    def tokenize(example):
        prompt = ""
        for msg in example["messages"]:
            prompt += f"{msg['role'].capitalize()}: {msg['content']}\n"
        tokenized = tokenizer(
            prompt,
            truncation=True,
            padding="max_length",  # or "longest"
            max_length=1024,
            return_tensors=None
        )
        tokenized["labels"] = tokenized["input_ids"].copy()
        return tokenized

    tokenized_dataset = dataset.map(tokenize, batched=False, remove_columns=dataset.column_names)

    # Data collator
    data_collator = DataCollatorForSeq2Seq(tokenizer, padding=True, return_tensors="pt")

    # Training arguments
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        num_train_epochs=3,
        save_strategy="epoch",
        save_total_limit=1,
        logging_steps=10,
        learning_rate=2e-4,
        bf16=True,
        remove_unused_columns=False,
        report_to="none",
    )

    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=data_collator,
        tokenizer=tokenizer,
    )
    # Resume from checkpoint if exists
    last_checkpoint = get_last_checkpoint(OUTPUT_DIR)
    trainer.train(resume_from_checkpoint=last_checkpoint)

    # Save model
    print(f"\n📂 Saving model to: {OUTPUT_DIR}")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    from pathlib import Path    
    print("📄 Output dir contents:")
    for path in Path(OUTPUT_DIR).glob("*"):
        print("-", path.name)


if __name__ == "__main__":
    main()