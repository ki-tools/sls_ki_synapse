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
