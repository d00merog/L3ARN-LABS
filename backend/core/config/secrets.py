import os
from typing import Optional

try:
    import hvac
except ImportError:  # hvac not installed
    hvac = None


def _vault_client() -> Optional["hvac.Client"]:
    """Initialize HashiCorp Vault client if configuration is present."""
    url = os.getenv("VAULT_ADDR")
    token = os.getenv("VAULT_TOKEN")
    if hvac and url and token:
        return hvac.Client(url=url, token=token)
    return None


def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """Retrieve secret from Docker secret file, Vault, or environment variable."""
    # Docker secrets
    secret_path = f"/run/secrets/{key}"
    if os.path.exists(secret_path):
        with open(secret_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    # Vault lookup
    client = _vault_client()
    if client:
        try:
            response = client.secrets.kv.v2.read_secret_version(path=f"l3arn-labs/{key}")
            return response["data"]["data"].get(key, default)
        except Exception:
            pass

    # Fallback to environment variable
    return os.getenv(key, default)
