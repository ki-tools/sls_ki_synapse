#!/usr/bin/env python3
import argparse
import sys
import os
import jwt

script_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(script_dir, '..'))
try:
    from core.auth import Auth
except Exception as ex:
    print('WARNING: Failed to load auth: {0}'.format(ex))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('secret', help='The secret to build the JWT with.')
    parser.add_argument('api_key', metavar='api-key',
                        help='The API key to encode in the token.')
    args = parser.parse_args()

    token = Auth.encode_jwt(args.secret, args.api_key)
    print('Token: {0}'.format(token))


if __name__ == "__main__":
    main()
