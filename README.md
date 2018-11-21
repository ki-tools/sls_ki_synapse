# SLS KI Synapse

[![Build Status](https://travis-ci.com/pcstout/sls_ki_synapse.svg?branch=master)](https://travis-ci.com/pcstout/sls_ki_synapse)

## Overview

A [Serverless](https://serverless.com/framework/docs/getting-started) application that runs on [AWS Lambda](https://aws.amazon.com/lambda) exposing a [GraphQL](https://graphql.org) interface for maintaining Rallies in [Synapse](https://www.synapse.org).

Capabilities:

- [Create a Rally](tests/handlers/test_json/create_rally.json)
- [Get a Rally](tests/handlers/test_json/get_rally.json)
- [Create a Rally Sprint](tests/handlers/test_json/create_rally_sprint.json)
- [Get a Rally Sprint](tests/handlers/test_json/get_rally_sprint.json)

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

- Populate SSM with the environment variables. This only needs to be done once or when the files/values change. See the [Authentication](#authentication) section for generating secrets and API keys.
  - `./scripts/set_ssm.py <service-stage>` 
    - Example: `./scripts/set_ssm.py production`
- Deploy to AWS
  - `sls deploy`
  
## Authentication

Authentication will be done via API Gateway with a Lambda function.
Initially a simple JWT authentication mechanism will be used to secure this service. A more robust authentication system will be implemented at a later date.
A secret will be stored in an environment variable along with a comma separated list of API keys.

```shell
JWT_SECRET=my-secret-string
JWT_API_KEYS=key1,key2,key3
```

The process for allowing a client access to the service is as follows:

1. Generate a secret key and an API key by running [gen_key.py](scripts/gen_key.py).
   1.1 Add the keys to your `private.ssm.env.json` file.
   1.2 Update SSM: `./scripts/set_ssm.py <service-stage>`
2. Generate a JWT for the client by running [gen_jwt.py](scripts/gen_jwt.py). Use the secret and API key generated above.

## Manual Testing

- View Logs: `sls logs -f graphql --tail`
- Test Queries:
  - Create a Rally: `sls invoke -f graphql -p tests/handlers/test_json/create_rally.json`
  - Get a Rally:  `sls invoke -f graphql -p tests/handlers/test_json/get_rally.json`
  - Create a Rally Sprint: `sls invoke -f graphql -p tests/handlers/test_json/create_rally_sprint.json`
  - Get a Rally Sprint:  `sls invoke -f graphql -p tests/handlers/test_json/get_rally_sprint.json`
  - With curl: `curl -X POST -H 'Authorization: Bearer JWT_TOKEN_HERE' --data 'QUERY_HERE' ENDPOINT_URL_HERE`
