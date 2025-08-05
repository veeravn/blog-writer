# services/model.py
import os, requests, json
import logging
from openai import AzureOpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Read the endpoint and key from env variables or fallback
AZURE_ML_ENDPOINT = os.getenv("AZURE_ML_ENDPOINT", "https://partha-style-endpoint.eastus.inference.ml.azure.com/score")
AZURE_ML_API_KEY = os.getenv("AZURE_ML_API_KEY")  # Set this in your .env file or deployment config
MODEL_NAME = "gpt-4.1"
DEPLOYMENT = "gpt-4.1"

def generate_with_model(prompt: str, temperature: float = 0.7, max_tokens: int = 300) -> str:
    if not AZURE_ML_API_KEY:
        raise ValueError("AZURE_ML_API_KEY not set in environment.")
    
    client = AzureOpenAI(
        api_version="2025-01-01-preview",
        azure_endpoint=AZURE_ML_ENDPOINT,
        api_key=AZURE_ML_API_KEY,
    )

    payload = build_prompt(prompt, "neutral")

    try:
        response = client.chat.completions.create(
            messages=payload,
            max_completion_tokens=13107,
            temperature=temperature,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            model=DEPLOYMENT
        )

        content = response.choices[0].message.content
        output = str(content)

        # Optionally remove the prompt from the start (if model echoes it)
        if output.lower().startswith(prompt.lower()):
            output = output[len(prompt):].strip()
        logging.info(f"Model response: {output[:100]}...")  # Log first 100 chars for brevity
        return output
    except requests.exceptions.RequestException as e:
        return {"error": f"🔥 Error calling deployed model: {e}"}

def build_prompt(prompt: str, tone: str = None, structure: str = None):
    system_msg = "You are a helpful assistant that writes clear and engaging blog posts."
    if tone or structure:
        tone = tone or "neutral"
        structure = structure or "paragraph form"
    messages=[
        {
            "role": "system",
            "content": system_msg,
        },
        {
            "role": "user",
            "content": f"{prompt}",
        },
        {
            "role": "assistant",
            "content": f"Write with a {tone} tone and the following structure: {structure}"
        }
    ]
    return messages