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

import secrets
import argparse

def main():
    """
    Generates a random key.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('bytes', type=int, nargs='?', help='How many bytes to generate.', default=64)
    args = parser.parse_args()

    print(secrets.token_hex(args.bytes))


if __name__ == "__main__":
    main()
