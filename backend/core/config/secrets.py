import os
from typing import Optional
import logging
from functools import lru_cache

try:
    import hvac
    from hvac.exceptions import VaultError
except ImportError:  # hvac not installed
    hvac = None
    VaultError = None

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _vault_client() -> Optional["hvac.Client"]:
    """Initialize HashiCorp Vault client if configuration is present."""
    url = os.getenv("VAULT_ADDR")
    token = os.getenv("VAULT_TOKEN")

    if not (hvac and url and token):
        logger.debug("Vault client not configured.")
        return None

    try:
        client = hvac.Client(url=url, token=token)
        if client.is_authenticated():
            logger.info("Vault client authenticated successfully.")
            return client
        logger.warning("Vault authentication failed.")
    except Exception as e:
        logger.error(f"Vault client initialization failed: {e}", exc_info=True)

    return None


def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Retrieve secret from Docker secret file, Vault, or environment variable.
    Order of precedence:
    1. Docker Secrets
    2. HashiCorp Vault
    3. Environment variables
    """
    # 1. Docker secrets
    secret_path = f"/run/secrets/{key}"
    if os.path.exists(secret_path):
        with open(secret_path, "r", encoding="utf-8") as f:
            secret_value = f.read().strip()
            logger.debug(f"Secret '{key}' loaded from Docker secret.")
            return secret_value

    # 2. Vault lookup
    client = _vault_client()
    if client:
        mount_point = os.getenv("VAULT_MOUNT_POINT", "secret")
        secret_path = os.getenv("VAULT_SECRET_PATH", f"l3arn-labs/{key}")
        try:
            response = client.secrets.kv.v2.read_secret_version(
                path=secret_path, mount_point=mount_point
            )
            if response and "data" in response and "data" in response["data"]:
                secret_value = response["data"]["data"].get(key)
                if secret_value:
                    logger.debug(f"Secret '{key}' loaded from Vault.")
                    return secret_value
        except VaultError as e:
            logger.warning(
                f"Could not retrieve secret '{key}' from Vault path "
                f"'{mount_point}/{secret_path}': {e}",
                exc_info=True,
            )
        except Exception:
            # Catch other potential exceptions, e.g., network issues
            pass

    # 3. Fallback to environment variable
    env_value = os.getenv(key, default)
    if env_value is not default:
        logger.debug(f"Secret '{key}' loaded from environment variable.")
    return env_value
