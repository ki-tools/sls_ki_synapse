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
import tempfile
import os
import json
import time
from tests.synapse_test_helper import SynapseTestHelper
from core import Synapse
from synapseclient import EntityViewSchema, EntityViewType, Column


# Load Environment variables.
test_env_file = 'private.test.env.json'

if os.path.isfile(test_env_file):
    with open('private.test.env.json') as f:
        config = json.load(f).get('test')

        # Validate required properties are present
        for prop in['SYNAPSE_USERNAME', 'SYNAPSE_PASSWORD']:
            if not prop in config or not config[prop]:
                raise Exception(
                    'Property: "{0}" is missing in private.test.env.json'.format(prop))

        for key, value in config.items():
            os.environ[key] = value
else:
    print('WARNING: Test environment file not found at: {0}'.format(
        test_env_file))


@pytest.fixture(scope='session')
def syn_client():
    return Synapse.client()


@pytest.fixture()
def syn_test_helper():
    """
    Provides the SynapseTestHelper as a fixture per function.
    """
    helper = SynapseTestHelper()
    yield helper
    helper.dispose()


@pytest.fixture
def temp_file(syn_test_helper):
    """
    Generates a temp file containing the SynapseTestHelper.uniq_name per function.
    """
    fd, tmp_filename = tempfile.mkstemp()
    with os.fdopen(fd, 'w') as tmp:
        tmp.write(syn_test_helper.uniq_name())
    yield tmp_filename

    if os.path.isfile(tmp_filename):
        os.remove(tmp_filename)
