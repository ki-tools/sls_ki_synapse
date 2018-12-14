# SLS KI Synapse

[![Build Status](https://travis-ci.com/pcstout/sls_ki_synapse.svg?branch=master)](https://travis-ci.com/pcstout/sls_ki_synapse)
[![Coverage Status](https://coveralls.io/repos/github/pcstout/sls_ki_synapse/badge.svg?branch=master)](https://coveralls.io/github/pcstout/sls_ki_synapse?branch=master)

## Overview

A [Serverless](https://serverless.com/framework/docs/getting-started) application that runs on [AWS Lambda](https://aws.amazon.com/lambda) exposing a [GraphQL](https://graphql.org) interface for maintaining Sprints in [Synapse](https://www.synapse.org).

Capabilities:

- Project:
  - [Create](tests/handlers/test_json/create_syn_project.json)
  - [Update](tests/handlers/test_json/update_syn_project.json)
  - [Query](tests/handlers/test_json/get_syn_project.json)
- Slide Deck:
  - [Create](tests/handlers/test_json/create_slide_deck.json)

## Development Setup

- [Install the Serverless Framework](https://serverless.com/framework/docs/providers/aws/guide/quick-start)
  - `npm install -g serverless`
  - Configure your AWS credentials by following [these directions](https://serverless.com/framework/docs/providers/aws/guide/credentials)
- Install Serverless Plugins:
  - `npm install`
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
  - `./scripts/set_ssm.py --stage <service-stage>` 
    - Example: `./scripts/set_ssm.py --stage production`
  - See the [Authentication](#authentication) section for generating secrets and API keys.
- Create the `A` records in Route53 if using a custom domain. This only needs to be done once for each stage.
  - `sls create_domain --stage <stage>`
    - Example: - `sls create_domain --stage production` 
  - See [serverless-domain-manager](https://github.com/amplify-education/serverless-domain-manager) for more details on configuring your custom domain.
- Deploy to AWS
  - `sls deploy --stage <stage>`
    - Example: - `sls deploy --stage production`
  
## Authentication

Authentication will be done using [API Gateway Lambda Authorizers](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-use-lambda-authorizer.html).

Initially a simple JWT authentication mechanism will be used to secure this service. A more robust authentication system will be implemented at a later date.

A secret will be stored in an environment variable along with a comma separated list of API keys.

```shell
JWT_SECRET=my-secret-string
JWT_API_KEYS=key1,key2,key3
```

The process for allowing a client access to the service is as follows:

1. Generate a secret key and an API key by running [gen_key.py](scripts/gen_key.py).
   - Add the keys to your `private.ssm.env.json` file.
   - Update SSM: `./scripts/set_ssm.py --stage <service-stage>`
2. Generate a JWT for the client by running [gen_jwt.py](scripts/gen_jwt.py). Use the secret and API key generated above.

## Manual Testing

- View Logs: `sls logs -f graphql --tail`
- Test Queries:
  - Project:
    - Create: `./scripts/json_to_gql.py tests/handlers/test_json/create_syn_project.json | sls invoke -f graphql`
    - Update: `./scripts/json_to_gql.py tests/handlers/test_json/update_syn_project.json | sls invoke -f graphql`
    - Query:  `./scripts/json_to_gql.py tests/handlers/test_json/get_syn_project.json | sls invoke -f graphql`
  - Slide Deck:
    - Create:  `./scripts/json_to_gql.py tests/handlers/test_json/create_slide_deck.json | sls invoke -f graphql`
  - With curl: `curl -X POST -H 'Authorization: Bearer JWT_TOKEN_HERE' --data 'QUERY_HERE' ENDPOINT_URL_HERE`
