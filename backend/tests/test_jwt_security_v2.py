from datetime import timedelta
import jwt
import pytest
from app.core.config import settings
from app.core.security import create_access_token, verify_token


def test_token_roundtrip():
    assert verify_token(create_access_token({"sub": "synthetic-user"}))["sub"] == "synthetic-user"


def test_expired_token_rejected():
    with pytest.raises(jwt.ExpiredSignatureError):
        verify_token(create_access_token({"sub": "synthetic-user"}, timedelta(seconds=-60)))


def test_missing_expiry_rejected():
    token = jwt.encode({"sub": "synthetic-user"}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    with pytest.raises(jwt.MissingRequiredClaimError):
        verify_token(token)


def test_wrong_signature_rejected():
    token = jwt.encode({"sub": "synthetic-user", "exp": 4102444800}, "unrelated-test-key-not-used-for-production", algorithm=settings.ALGORITHM)
    with pytest.raises(jwt.InvalidSignatureError):
        verify_token(token)


def test_unsigned_token_rejected():
    token = jwt.encode({"sub": "synthetic-user", "exp": 4102444800}, None, algorithm="none")
    with pytest.raises(jwt.InvalidTokenError):
        verify_token(token)
