# Copyright 2018-present, Bill & Melinda Gates Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
