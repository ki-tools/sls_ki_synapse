import pytest
import tempfile
import os
import json
import boto3
from src.core import Config

# Load Environment variables.
Config.load_local_into_env('private.test.env.json', stage=Config.Stages.TEST)

# Import the remaining modules after the test ENV variables have been loaded and set.
from synapse_test_helper import SynapseTestHelper
from src.handlers import graphql_handler
from src.core import Synapse


@pytest.fixture(scope='session', autouse=True)
def syn_client():
    SynapseTestHelper.configure(Synapse.client())
    return Synapse.client()


@pytest.fixture()
def synapse_test_helper():
    """Provides the SynapseTestHelper as a fixture per function."""
    with SynapseTestHelper() as sth:
        yield sth


@pytest.fixture(scope='session')
def s3_client():
    return boto3.client('s3')


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
