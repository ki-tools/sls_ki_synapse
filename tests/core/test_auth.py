import pytest
import jwt
from core import Auth


def test_authenticate(monkeypatch):
    secret = 'abc'
    api_keys = '1,12,123'
    monkeypatch.setenv('JWT_SECRET', secret)
    monkeypatch.setenv('JWT_API_KEYS', api_keys)

    token = Auth.encode_jwt(secret, '1')
    assert Auth.authenticate(token) != None


def test_encode_decode_jwt(monkeypatch):
    secret = 'abc'
    api_key = '1'
    monkeypatch.setenv('JWT_SECRET', secret)
    monkeypatch.setenv('JWT_API_KEYS', api_key)

    token = Auth.encode_jwt(secret, api_key)
    decoded = Auth.decode_jwt(token, secret)
    assert decoded['apiKey'] == api_key
