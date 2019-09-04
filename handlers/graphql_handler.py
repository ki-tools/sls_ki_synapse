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
