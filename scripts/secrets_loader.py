# secrets_loader.py

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def get_env_vars(vault_name: str, secret_names: list[str]) -> dict:
    key_vault_url = f"https://{vault_name}.vault.azure.net/"
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=key_vault_url, credential=credential)

    env_vars = {}
    for secret in secret_names:
        try:
            secret_name = secret.upper().replace("-", "_")
            env_vars[secret_name] = client.get_secret(secret).value
        except Exception as e:
            print(f"⚠️ Failed to retrieve {secret}: {e}")
    return env_vars
