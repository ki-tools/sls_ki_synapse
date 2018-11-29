#!/usr/bin/env python3
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
