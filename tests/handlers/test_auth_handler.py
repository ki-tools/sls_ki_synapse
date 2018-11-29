import pytest
from handlers import auth_handler
from core import Auth
import json


def test_authenticate(monkeypatch):
    secret = 'abc'
    api_keys = 'valid-token'
    monkeypatch.setenv('JWT_SECRET', secret)
    monkeypatch.setenv('JWT_API_KEYS', api_keys)

    # Allow
    token = Auth.encode_jwt(secret, 'valid-token')
    arn = 'a-test-arn'

    event = {
        'authorizationToken': 'Bearer {0}'.format(token),
        'methodArn': arn
    }
    resp = auth_handler.authenticate(event, None)
    assert resp['policyDocument']['Statement'][0]['Effect'] == 'Allow'

    # Deny
    token = Auth.encode_jwt(secret, 'invalid-token')

    event = {
        'authorizationToken': token,
        'methodArn': arn
    }
    resp = auth_handler.authenticate(event, None)
    assert resp['policyDocument']['Statement'][0]['Effect'] == 'Deny'
