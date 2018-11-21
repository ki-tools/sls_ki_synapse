import core.log
import logging
from core.auth import Auth


def generatePolicy(principalId, effect, methodArn):
    authResponse = {}
    authResponse['principalId'] = principalId

    if effect and methodArn:
        policyDocument = {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': 'execute-api:Invoke',
                    'Effect': effect,
                    'Resource': methodArn
                }
            ]
        }

        authResponse['policyDocument'] = policyDocument

    return authResponse


def authenticate(event, context):
    logging.debug('Event Received: authenticate')

    token = event['authorizationToken']

    api_key = Auth.authenticate(token)

    if api_key:
        logging.debug('Event Response: Allow')
        return generatePolicy(api_key, 'Allow', event['methodArn'])
    else:
        logging.debug('Event Response: Deny')
        return generatePolicy(None, 'Deny', event['methodArn'])
