#!/usr/bin/env python3

import argparse
import json


def main():
    """
    Transforms a JSON file into a GraphQL request.
    Usage for invoking a function:
        ./scripts/json_to_gql.py path/to/file.json | sls invoke -f graphql
    With specific variables:
        ./scripts/json_to_gql.py path/to/file.json id="my-id" name="new name" | sls invoke -f graphql
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='The JSON file to transform')
    args, variables = parser.parse_known_args()

    with open(args.file) as f:
        j = json.load(f)
        if variables:
            for prop in variables:
                split = prop.split('=')
                j['variables'][split[0]] = split[1]
        print(json.dumps({'body': json.dumps(j)}))


if __name__ == "__main__":
    main()
