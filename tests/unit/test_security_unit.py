# tests/unit/test_security_unit.py
import pytest

from app.core import security


def test_password_hash_and_verify():
    raw = "secret123"
    h = security.hash_password(raw)
    assert h != raw
    assert security.verify_password(raw, h) is True
    assert security.verify_password("wrong", h) is False


def test_access_token_payload_roundtrip():
    token = security.create_access_token("42")
    payload = security.decode_token(token)

    assert payload["sub"] == "42"
    assert payload["type"] == "access"
    assert payload["exp"] > payload["iat"]


def test_refresh_token_payload_roundtrip():
    token = security.create_refresh_token("42")
    payload = security.decode_token(token)

    assert payload["sub"] == "42"
    assert payload["type"] == "refresh"
    assert payload["exp"] > payload["iat"]


def test_decode_token_invalid_raises():
    with pytest.raises(Exception):
        security.decode_token("not-a-jwt-token")
