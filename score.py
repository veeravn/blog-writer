import os, json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Load environment variables or hardcoded defaults
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = None
tokenizer = None

def init():
    global model, tokenizer

    # Azure ML mounts model to this path
    model_path = os.path.join(os.environ.get("AZUREML_MODEL_DIR", "./"), "merged_model")

    print("🔍 Loading merged model from:", model_path)

    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
        device_map="auto",  # Automatically assigns model layers to available devices
        trust_remote_code=True,
    )

    model.eval()
    print("✅ Merged model and tokenizer loaded successfully.")

def run(input_data):
    """
    input_data is a JSON object like:
    {
        "prompt": "Write a blog post about...",
        "max_new_tokens": 300,
        "temperature": 0.7
    }
    """
    try:
        # Convert JSON string to dict
        if isinstance(input_data, str):
            input_data = json.loads(input_data)
        prompt = input_data.get("prompt", "")
        max_new_tokens = input_data.get("max_new_tokens", 300)
        temperature = input_data.get("temperature", 0.7)

        inputs = tokenizer(prompt, return_tensors="pt").to(DEVICE)
        with torch.no_grad():
            output = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=True,
                top_p=0.95,
                top_k=50,
                pad_token_id=tokenizer.eos_token_id
            )
        generated = tokenizer.decode(output[0], skip_special_tokens=True)
        return json.dumps({"output": generated[len(prompt):].strip()})  # Return only the generated continuation

    except Exception as e:
        return f"🔥 Error during inference: {str(e)}"
