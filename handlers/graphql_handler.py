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

import os
import sys
import json
from core.log import logger
from data import schema
from graphql_server import (
    run_http_query,
    encode_execution_results,
    default_format_error
)


def graphql(event, context):
    """
    Handles the graphql event.
    """
    logger.debug('Event Received: graphql: {}'.format(json.dumps(event)))

    body = json.loads(event['body'])

    # Execute the GraphQL query.
    execution_results, _ = run_http_query(schema.root(), 'post', body)

    # Get the results and status code for the response.
    result, status_code = encode_execution_results(
        execution_results, default_format_error, False, lambda o: o)

    # Build the response with the status code and GraphQL results.
    response = {
        'statusCode': status_code,
        'headers': {
            'Access-Control-Allow-Origin': "*",
            'Access-Control-Allow-Credentials': 'true'
        },
        'body': json.dumps(result)
    }

    logger.debug('Event Response: graphql: {}'.format(json.dumps(response)))

    return response
