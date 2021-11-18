#!/usr/bin/env python3

import argparse
import sys
import os

script_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(script_dir, '..'))
try:
    from core.auth import Auth
    from core.config import Config
except Exception as ex:
    print('WARNING: Failed to load imports: {0}'.format(ex))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--api-key', help='The API key to encode in the token.')
    parser.add_argument('--secret', help='The secret to build the JWT with.')
    parser.add_argument('--stage',
                        choices=Config.Stages.ALL,
                        help='The stage to load from the config file')
    args = parser.parse_args()

    api_keys = []

    api_key = args.api_key
    secret = args.secret
    stage = args.stage
    if stage:
        print('Loading secret and API keys from configuration for: {0}'.format(stage))
        ssm_config = Config.open_local('private.ssm.env.json', stage=stage)
        secret = ssm_config['JWT_SECRET']
        if not api_key:
            api_keys = ssm_config['JWT_API_KEYS'].split(',')
    else:
        if not api_key and not secret:
            print('Secret and API key are required when not using --stage.')
            return
        api_keys.append(api_key)

    for key in api_keys:
        token = Auth.encode_jwt(secret, key)
        print('-' * 80)
        print('API Key: {0}'.format(key))
        print('JWT: {0}'.format(token))


if __name__ == "__main__":
    main()
