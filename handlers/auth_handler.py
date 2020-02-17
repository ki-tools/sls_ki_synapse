from core import Auth
from core.log import logger


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
    logger.debug('Event Received: authenticate')

    token = event['authorizationToken'].replace('Bearer ', '')

    api_key = Auth.authenticate(token)

    if api_key:
        logger.debug('Event Response: Allow')
        return generatePolicy(api_key, 'Allow', event['methodArn'])
    else:
        logger.debug('Event Response: Deny')
        return generatePolicy(None, 'Deny', event['methodArn'])
