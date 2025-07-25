import logging
import os
from .model import generate_with_model

if os.getenv("AZURE_FUNCTIONS_ENVIRONMENT") != "Production":
    from dotenv import load_dotenv
    load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def generate_blog_post(prompt: str, style: str = None, preferences: dict = None) -> str:
    # System prompt injection
    if preferences:
        tone = preferences.get("tone", "default")
        structure = preferences.get("structure", "blog")
        system_prompt = f"Write with a {tone} tone and {structure} structure.\n"
    elif style:
        system_prompt = f"Write in the style of {style}.\n"
    else:
        system_prompt = ""

    full_prompt = system_prompt + prompt
    return generate_with_model(full_prompt)

def revise_blog_post(original: str, feedback: str, preferences: dict = None) -> str:
    tone = preferences.get("tone", "confident") if preferences else "confident"
    
    system_prompt = f"You are a helpful writing assistant. Revise the blog post with a {tone} tone based on the feedback below.\n\n"
    prompt = (
        f"{system_prompt}"
        f"Original Post:\n{original}\n\n"
        f"Feedback:\n{feedback}\n\n"
        f"Revised Post:"
    )
    
    return generate_with_model(prompt, temperature=0.5, max_tokens=800)