import pytest
import tempfile
import os
import json
import boto3
from core import Config

# Load Environment variables.
Config.load_local_into_env('private.test.env.json', stage=Config.Stages.TEST)

# Import the remaining modules after the test ENV variables have been loaded and set.
from tests.synapse_test_helper import SynapseTestHelper
from handlers import graphql_handler
from core import Synapse


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


@pytest.fixture(scope='session')
def s3_client():
    return boto3.client('s3')


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


@pytest.fixture(scope='session')
def do_gql_post():
    """
    Executes a query against the handler.
    """

    def _do_gql_post(query, variables):
        event = {'body': json.dumps({'query': query, 'variables': variables})}
        context = None
        response = graphql_handler.graphql(event, context)

        # Convert the body to a dict so testing is easier.
        response['body'] = json.loads(response['body'])

        return response

    yield _do_gql_post
