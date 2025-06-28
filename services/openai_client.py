import logging, openai, time, os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_type = os.getenv("OPENAI_API_TYPE", "openai")
openai.api_version = os.getenv("OPENAI_API_VERSION", None)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

MAX_RETRIES = 3
RETRY_DELAY = 2

revision_tools = [{
    "name": "revise_post",
    "description": "Make tone more confident",
    "parameters": {
        "type": "object",
        "properties": {
            "tone": {
                "type": "string",
                "enum": ["confident", "casual", "formal", "friendly", "professional"],
                "description": "Target tone for the revised blog post"
            }
        },
        "required": ["tone"]
    }
}]

def call_with_retry(openai_fn, *args, **kwargs):
    for attempt in range(MAX_RETRIES):
        try:
            return openai_fn(*args, **kwargs)
        except Exception as e:
            logger.warning(f"OpenAI API error: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
            else:
                raise

def generate_blog_post(prompt: str, style: str = None, preferences: dict = None) -> str:
    messages = [{"role": "user", "content": prompt}]
    if preferences:
        tone = preferences.get("tone", "default")
        structure = preferences.get("structure", "blog")
        messages.insert(0, {"role": "system", "content": f"Write with a {tone} tone and {structure} structure."})
    elif style:
        messages.insert(0, {"role": "system", "content": f"Write in the style of {style}."})
    response = call_with_retry(openai.ChatCompletion.create,
                               model="gpt-4",
                               messages=messages,
                               temperature=0.7)
    return response.choices[0].message["content"]

def revise_blog_post(original: str, feedback: str, preferences: dict = None) -> str:
    tone = preferences.get("tone", "confident") if preferences else "confident"
    messages = [
        {"role": "system", "content": "You are a helpful writing assistant. Apply the feedback to improve the post."},
        {"role": "user", "content": f"Original Post:\n{original}"},
        {"role": "user", "content": f"Feedback:\n{feedback}"}
    ]
    response = call_with_retry(openai.ChatCompletion.create,
                               model="gpt-4",
                               messages=messages,
                               temperature=0.5,
                               functions=revision_tools,
                               function_call={"name": "revise_post"})
    message = response.choices[0].message
    if message.get("function_call"):
        logger.info(f"Function call: {message['function_call']}")
    return message.get("content", "[No content returned]")
