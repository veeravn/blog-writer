# services/model.py
import os, requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

    logging.info(f"Calling Azure ML endpoint: {AZURE_ML_ENDPOINT}")
    logging.info(f"Payload: {payload}")

    try:
        response = requests.post(AZURE_ML_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
        # Attempt to parse JSON
        try:
            resp_json = response.json()
            if "output" in resp_json:
                output = resp_json["output"]
            elif "outputs" in resp_json:
                output = resp_json["outputs"]
            else:
                # Fallback: just dump the json
                output = str(resp_json)
        except Exception:
            # Fallback: treat as plain text
            output = response.text.strip()

        # Optionally remove the prompt from the start (if model echoes it)
        if output.lower().startswith(prompt.lower()):
            output = output[len(prompt):].strip()
        return output
    except requests.exceptions.RequestException as e:
        return {"error": f"🔥 Error calling deployed model: {e}"}

def build_prompt(prompt: str, tone: str = None, structure: str = None):
    system_msg = "You are a helpful assistant that writes clear and engaging blog posts."
    if tone or structure:
        tone = tone or "neutral"
        structure = structure or "paragraph form"
        system_msg += f" Write with a {tone} tone and {structure} structure."

    formatted_prompt = f"{prompt}"
    return formatted_prompt