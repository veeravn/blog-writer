import logging
from .model import generate_with_model

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def generate_blog_post(prompt: str, style_description: str = None, preferences: dict = None) -> str:
    # System prompt injection
    system_prompt = ""
    if preferences:
        tone = preferences.get("tone", "default")
        structure = preferences.get("structure", "blog")
        system_prompt += f"Write with a {tone} tone and {structure} structure.\n"
    if style_description:
        system_prompt += f"Emulate the following writing style: {style_description}\n"
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