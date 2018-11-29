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
import os
from moto import mock_ssm
from core import ParamStore


@pytest.fixture
def key():
    return 'TEST_KEY'


@pytest.fixture
def value():
    return 'TEST_VALUE'


@mock_ssm
def test_get(key, value, monkeypatch):
    assert os.environ.get(key) == None
    assert ParamStore._get_from_os(key) == None
    assert ParamStore._get_from_ssm(key) == None
    assert ParamStore.get(key) == None

    # From OS
    monkeypatch.setenv(key, value)
    assert os.environ.get(key) == value
    assert ParamStore.get(key) == value

    monkeypatch.delenv(key, value)
    assert os.environ.get(key) == None
    assert ParamStore.get(key) == None

    # From SSM
    ParamStore._set_ssm_parameter(key, value)
    assert ParamStore.get(key) == value


@mock_ssm
def test__get_from_os(key, value, monkeypatch):
    assert os.environ.get(key) == None
    assert ParamStore._get_from_os(key) == None
    assert ParamStore._get_from_ssm(key) == None
    assert ParamStore.get(key) == None

    monkeypatch.setenv(key, value)
    assert os.environ.get(key) == value
    assert ParamStore._get_from_os(key) == value


@mock_ssm
def test__get_from_ssm(key, value):
    assert os.environ.get(key) == None
    assert ParamStore._get_from_os(key) == None
    assert ParamStore._get_from_ssm(key) == None
    assert ParamStore.get(key) == None

    ParamStore._set_ssm_parameter(key, value)
    assert ParamStore._get_from_ssm(key) == value


@mock_ssm
def test__set_ssm_parameter(key, value):
    assert os.environ.get(key) == None
    assert ParamStore._get_from_ssm(key) == None

    ParamStore._set_ssm_parameter(key, value)
    assert ParamStore._get_from_ssm(key) == value


def test__build_ssm_key(monkeypatch):
    monkeypatch.setenv('SERVICE_NAME', 'a')
    monkeypatch.setenv('SERVICE_STAGE', 'b')
    assert ParamStore._build_ssm_key('c') == '/a/b/c'
