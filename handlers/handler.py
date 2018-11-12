import json as JSON
from core.log import logging
from data import schema
from graphql_server import (
    run_http_query, encode_execution_results, default_format_error)


def graphql(event, context):
    """
    Handles the graphql event.
    """
    logging.debug('Event Received: {}'.format(JSON.dumps(event)))

    execution_results, _ = run_http_query(schema.root(), 'post', event)
    result, status_code = encode_execution_results(
        execution_results, default_format_error, False, lambda o: o)

    response = {
        'statusCode': status_code
    }

    response.update(result)

    logging.debug('Event Response: {}'.format(JSON.dumps(response)))

    return response
