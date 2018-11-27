import os
import sys
import json
from core import log
import logging
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
    logging.debug('Event Received: graphql: {}'.format(json.dumps(event)))

    # Execute the GraphQL query.
    execution_results, _ = run_http_query(schema.root(), 'post', event)

    # Get the results and status code for the response.
    result, status_code = encode_execution_results(
        execution_results, default_format_error, False, lambda o: o)

    # Build the response with the status code and GraphQL results.
    response = {
        'statusCode': status_code
    }
    response.update(result)

    # JSON encode the response.
    json_response = json.dumps(response)

    logging.debug('Event Response: graphql: {}'.format(json_response))

    return json_response
