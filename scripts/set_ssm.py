#!/usr/bin/env python3

import json
import argparse
import sys
import os
import yaml
from sls_tools.param_store import ParamStore

script_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(script_dir, '..'))
try:
    from core.env import Env
except Exception as ex:
    print('WARNING: Failed to load param_store: {0}'.format(ex))


def load_json(path):
    with open(path) as f:
        return json.load(f)


def load_yaml(path):
    with open(path) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def import_into_ssm(service_name, stage):
    """
    Imports the key/values from private.ssm.env.json into SSM.
    """
    # Set the service variables so Env works correctly.
    os.environ['SERVICE_NAME'] = service_name
    os.environ['SERVICE_STAGE'] = stage

    print('Setting SSM Values for: {0}'.format(stage))
    print('')

    # Load the deploy variables so the AWS connection is available.
    deploy_config = load_json(os.path.join(
        script_dir, '..', 'private.sls.deploy.json')).get(stage)
    for key, value in deploy_config.items():
        if isinstance(value, bool):
            value = str(value).lower()
        elif not isinstance(value, str):
            value = str(value)
        os.environ[key] = value

    # Set the key/values.
    ssm_config = load_json(os.path.join(
        script_dir, '..', 'private.ssm.env.json')).get(stage)
    for key, value in ssm_config.items():
        print('')
        print(key)

        if value:
            current_value = ParamStore.get(key, store=ParamStore.Stores.SSM).value
            if current_value != value:
                ParamStore.set(key, value, store=ParamStore.Stores.SSM)
                print('  - Value has been set to: {0}'.format(value))
            else:
                print('  - Key/value already set.')
        else:
            print('  - WARNING: Key value not set in configuration file. Key/value NOT set in SSM.')

    print('')


def get_service_name():
    """
    Gets the service name from serverless.yml
    """
    service_name = None
    yml = load_yaml(os.path.join(script_dir, '..', 'serverless.yml'))

    if isinstance(yml['service'], dict):
        service_name = yml['service']['name']
    else:
        service_name = yml['service']

    return service_name


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--stage',
                        choices=['production', 'staging', 'dev', 'test'],
                        help='The deploy stage.',
                        default='dev')
    args = parser.parse_args()

    service_name = get_service_name()

    import_into_ssm(service_name, args.stage)


if __name__ == "__main__":
    main()
