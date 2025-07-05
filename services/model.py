# services/model.py
import os, requests
import torch

# Read the endpoint and key from env variables or fallback
AZURE_ML_ENDPOINT = os.getenv("AZURE_ML_ENDPOINT", "https://partha-style-endpoint.eastus.inference.ml.azure.com/score")
AZURE_ML_API_KEY = os.getenv("AZURE_ML_API_KEY")  # Set this in your .env file or deployment config


def generate_with_model(prompt: str, temperature: float = 0.7, max_tokens: int = 512) -> str:
    if not AZURE_ML_API_KEY:
        raise ValueError("AZURE_ML_API_KEY not set in environment.")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AZURE_ML_API_KEY}"
    }

    payload = {
        "prompt": build_prompt(prompt, "neutral"),
        "max_new_tokens": max_tokens,
        "temperature": temperature
    }

    try:
        response = requests.post(AZURE_ML_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
        output = response.text.strip()
        if output.lower().startswith(prompt.lower()):
            output = output[len(prompt):].strip()
        return output
    except requests.exceptions.RequestException as e:
        return f"🔥 Error calling deployed model: {e}"

def build_prompt(prompt: str, tone: str = None, structure: str = None):
    system_msg = "You are a helpful assistant that writes clear and engaging blog posts."
    if tone or structure:
        tone = tone or "neutral"
        structure = structure or "paragraph form"
        system_msg += f" Write with a {tone} tone and {structure} structure."

    formatted_prompt = f"{system_msg}\nUser: {prompt}\nAssistant:"
    return formatted_prompt