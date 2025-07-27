import logging
from .model import generate_with_model
import json
# services/openai_client.py

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def generate_blog_post(
    prompt: str,
    style_description: str = None,
    preferences: dict = None,
    structure: dict = None
) -> dict:
    # Build system prompt for explicit structure
    system_prompt = ""
    if preferences:
        tone = preferences.get("tone", "default")
        system_prompt += f"Write with a {tone} tone.\n"
    if style_description:
        system_prompt += f"Emulate this style: {style_description}\n"
    if structure:
        if structure.get("include_title"):
            system_prompt += "Begin with a compelling title.\n"
        if structure.get("include_headers"):
            system_prompt += "Use headers for each section.\n"
        sections = structure.get("sections")
        if sections:
            system_prompt += (
                "Organize the post into these sections: " +
                ", ".join(sections) + ".\n"
            )
        system_prompt += (
            "Return the output in JSON with keys: 'title' (str), 'sections' (list of objects with 'header' and 'content'), and 'full_text' (the entire post as a string)."
        )
    else:
        system_prompt += "Write a structured blog post."

    full_prompt = system_prompt + "\n" + prompt
    raw_output = generate_with_model(full_prompt)

    # Try to parse JSON if returned by the model, else fallback to full_text
    try:
        result = json.loads(raw_output)
    except Exception:
        result = {
            "title": None,
            "sections": [],
            "full_text": raw_output
        }
    return result

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