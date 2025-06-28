import tempfile
import os, uuid
from datetime import datetime
from typing import List, Dict
from .cosmos_db import save_prompt_history, fetch_user_preferences

def store_prompt_context(user_id: str, prompt: str, tone: str):
    entry = {
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat(),    
        "prompt": prompt,
        "preferred_tone": tone
    }
    save_prompt_history(entry)

def get_user_tone_preferences(user_id: str) -> Dict:
    return fetch_user_preferences(user_id)

def save_to_temp(file):
    temp_dir = tempfile.gettempdir()
    path = os.path.join(temp_dir, file.filename)
    with open(path, "wb") as f:
        f.write(file.file.read())
    return path

def apply_preferences_to_prompt(prompt, preferences):
    tone = preferences.get("tone", "")
    structure = preferences.get("structure", "")
    if tone:
        prompt = f"[Tone: {tone}] {prompt}"
    if structure:
        prompt = f"[Structure: {structure}] {prompt}"
    return prompt
