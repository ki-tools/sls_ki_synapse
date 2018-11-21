#!/usr/bin/env python3
import json
import argparse
import sys
import os
import yaml

script_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(script_dir, '..'))
try:
    from core.param_store import ParamStore
except Exception as ex:
    print('WARNING: Failed to load param_store: {0}'.format(ex))


def load_json(path):
    with open(path) as f:
        return json.load(f)


def load_yaml(path):
    with open(path) as f:
        return yaml.load(f)


def import_into_ssm(service_name, stage):
    """
    Imports the key/values from private.ssm.env.json into SSM.
    """
    # Set the service variables so ParamStore works correctly.
    os.environ['SERVICE_NAME'] = service_name
    os.environ['SERVICE_STAGE'] = stage

    # Load the deploy variables so the AWS connection is available.
    deploy_config = load_json(os.path.join(
        script_dir, '..', 'private.sls.deploy.json')).get(stage)
    for key, value in deploy_config.items():
        os.environ[key] = value

    # Set the key/values.
    ssm_config = load_json(os.path.join(
        script_dir, '..', 'private.ssm.env.json')).get(stage)
    for key, value in ssm_config.items():
        print('Setting SSM Key: {0}, Value: {1}'.format(key, value))
        ParamStore._set_ssm_parameter(key, value)


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

    parser.add_argument('stage', nargs='?', choices=[
                        'production', 'staging', 'dev', 'test'], help='The deploy stage.', default='dev')
    args = parser.parse_args()

    service_name = get_service_name()

    import_into_ssm(service_name, args.stage)


if __name__ == "__main__":
    main()
