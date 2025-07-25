# services/memory.py

from services.blob_storage import save_json_to_blob, load_json_from_blob

PREFERENCES_CONTAINER = "memory"
PREFERENCES_BLOB_TEMPLATE = "{user_id}/preferences.json"

def get_preferences(user_id: str) -> dict:
    """
    Load the full preferences dictionary for a given user from blob storage.
    Returns an empty dict if not found.
    """
    blob_path = PREFERENCES_BLOB_TEMPLATE.format(user_id=user_id)
    return load_json_from_blob(PREFERENCES_CONTAINER, blob_path)


def save_preferences(user_id: str, prefs: dict):
    """
    Save the full preferences dictionary for a user to blob storage.
    """
    blob_path = PREFERENCES_BLOB_TEMPLATE.format(user_id=user_id)
    save_json_to_blob(PREFERENCES_CONTAINER, blob_path, prefs)

