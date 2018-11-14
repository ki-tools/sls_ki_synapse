# SLS KI Synapse

## Overview

A [Serverless](https://serverless.com/framework/docs/getting-started) application that runs on [AWS Lambda](https://aws.amazon.com/lambda) exposing a [GraphQL](https://graphql.org) interface for maintaining Rallies in [Synapse](https://www.synapse.org).

Capabilities:

- [Create a Rally](tests/handlers/test_json/create_rally.json)
- [Get a Rally](tests/handlers/test_json/get_rally.json)

## Development Setup

- [Install the Serverless Framework](https://serverless.com/framework/docs/providers/aws/guide/quick-start)
  - `npm install -g serverless`
  - Configure your AWS credentials by following [these directions](https://serverless.com/framework/docs/providers/aws/guide/credentials)
- Install Serverless Plugins:
  - `sls plugin install -n serverless-python-requirements`
- Create and activate a Virtual Environment:
  - `python3 -m venv .venv`
  - `source .venv/bin/activate` 
- Configure environment variables:
  - Copy each file in [templates](templates) into the project's root directory and edit each file to contain the correct values.
- Install Python Dependencies:
  - `pip install -r requirements.txt`
  - `pip install -r requirements-dev.txt`
- Run specs.
  - `pytest`

## Deploying

- Populate SSM with the environment variables. This only needs to be done once or when the files/values change.
  - `python scripts/set_ssm.py <service-stage>` 
    - Example: `python scripts/set_ssm.py production`
- Deploy to AWS
  - `sls deploy`

## Manual Testing

- View Logs: `sls logs -f graphql --tail`
- Test Queries:
  - Get a Rally:  `sls invoke -f graphql -p tests/handlers/test_json/get_rally.json`
  - Create a Rally: `sls invoke -f graphql -p tests/handlers/test_json/create_rally.json`
