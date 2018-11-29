#!/usr/bin/env python3

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
