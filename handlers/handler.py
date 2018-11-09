import json as JSON
from core.log import logging
from data import schema


def graphql(event, context):
    """
    Handles the graphql event.
    """
    logging.debug('Event Received: {}'.format(JSON.dumps(event)))

    response = schema.root().execute(event)

    logging.debug('Event Response: {}'.format(JSON.dumps(response)))

    return response
