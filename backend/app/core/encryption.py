"""Field-level encryption for sensitive data."""
import base64
import json
import os
from cryptography.fernet import Fernet
from app.core.config import settings


def get_fernet():
    key = settings.ENCRYPTION_KEY
    if not key:
        return None
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt_json(data: dict) -> str:
    f = get_fernet()
    if not f:
        return json.dumps(data)  # Fallback: no encryption in dev
    return f.encrypt(json.dumps(data).encode()).decode()


def decrypt_json(data: str) -> dict:
    f = get_fernet()
    if not f:
        return json.loads(data) if isinstance(data, str) else data
    try:
        return json.loads(f.decrypt(data.encode()).decode())
    except Exception:
        # Try plain JSON fallback for pre-encryption data
        if isinstance(data, (dict, list)):
            return data
        return json.loads(data)
