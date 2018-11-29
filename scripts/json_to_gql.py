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

import os
import argparse
import json


def main():
    """
    Transforms a JSON file into a GraphQL request.
    Usage for invoking a function: ./scripts/json_to_gql.py path/to/file.json | sls invoke -f graphql
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='The JSON file to transform')
    args = parser.parse_args()

    with open(args.file) as f:
        j = json.load(f)
        print(json.dumps({'body': json.dumps(j)}))


if __name__ == "__main__":
    main()
