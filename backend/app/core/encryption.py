"""Field-level encryption for sensitive data (OAuth tokens, API keys).

ENCRYPTION_KEY (Fernet) is REQUIRED in production. In development without a key,
encrypt/decrypt are no-ops with a loud warning so tokens can still be tested.
"""
import json
import logging
from cryptography.fernet import Fernet, InvalidToken
from app.core.config import settings

_logger = logging.getLogger(__name__)
_warned = False


def get_fernet():
    global _warned
    key = settings.ENCRYPTION_KEY
    if not key:
        if settings.ENVIRONMENT != "development" and not _warned:
            _logger.error(
                "ENCRYPTION_KEY is not set in a non-development environment! "
                "OAuth tokens will be stored UNENCRYPTED. "
                "Generate one: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
            )
            _warned = True
        elif not _warned:
            _logger.warning("ENCRYPTION_KEY not set — tokens stored unencrypted (dev mode)")
            _warned = True
        return None
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt_value(value: str) -> str:
    """Encrypt a string. Returns base64 ciphertext, or plaintext in dev without key."""
    if not value:
        return value
    f = get_fernet()
    if not f:
        return value
    return f.encrypt(value.encode()).decode()


def decrypt_value(value: str) -> str:
    """Decrypt a string. Handles pre-encryption plaintext gracefully (encrypt-on-read)."""
    if not value:
        return value
    f = get_fernet()
    if not f:
        return value
    try:
        return f.decrypt(value.encode()).decode()
    except (InvalidToken, Exception):
        # Pre-encryption plaintext — return as-is.
        # Caller should encrypt and save back on next write.
        _logger.info("Found pre-encryption plaintext token — will encrypt on next save")
        return value


def encrypt_json(data) -> str:
    """Encrypt a dict/list as JSON. Returns ciphertext or plain JSON in dev."""
    if data is None:
        return None
    f = get_fernet()
    raw = json.dumps(data) if not isinstance(data, str) else data
    if not f:
        return raw
    return f.encrypt(raw.encode()).decode()


def decrypt_json(data) -> dict:
    """Decrypt JSON. Handles pre-encryption plain JSON and dicts gracefully."""
    if data is None:
        return None
    if isinstance(data, (dict, list)):
        return data  # Already decoded (e.g. from JSON column)
    f = get_fernet()
    if not f:
        return json.loads(data) if isinstance(data, str) else data
    try:
        return json.loads(f.decrypt(data.encode()).decode())
    except (InvalidToken, Exception):
        # Pre-encryption plain JSON fallback
        try:
            return json.loads(data)
        except (json.JSONDecodeError, TypeError):
            _logger.error("Failed to decrypt or parse token data")
            return {}
