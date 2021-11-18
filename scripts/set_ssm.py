#!/usr/bin/env python3

import argparse
import sys
import os
import logging

logging.disable()

script_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(script_dir, '..'))
try:
    from core.config import Config
    from sls_tools.param_store import ParamStore
except Exception as ex:
    print('ERROR: Failed to load imports: {0}'.format(ex))


def import_into_ssm(stage, action):
    """
    Imports the key/values from private.ssm.env.json into SSM.
    """
    print('Setting SSM Values for: {0}'.format(stage))
    print('')

    service_name = get_service_name()

    # Set the service variables so Env works correctly.
    ParamStore.set('SERVICE_NAME', service_name, store=ParamStore.Stores.OS)
    ParamStore.set('SERVICE_STAGE', stage, store=ParamStore.Stores.OS)

    # Load the deploy variables so the AWS connection is available.
    Config.load_local_into_env('private.sls.deploy.json', stage=stage)

    # Set the key/values.
    ssm_config = Config.open_local('private.ssm.env.json', stage=stage, for_env=True)
    for key, value in ssm_config.items():
        print('')
        print(key)

        if action == 'import':
            if value:
                current_value = ParamStore.get(key, store=ParamStore.Stores.SSM).value
                if current_value != value:
                    ParamStore.set(key, value, store=ParamStore.Stores.SSM)
                    print('  - Value has been set to: {0}'.format(value))
                else:
                    print('  - Key/value already set.')
            else:
                print('  - WARNING: Key value not set in configuration file. Key/value NOT set in SSM.')
        else:
            if ParamStore.contains(key, store=ParamStore.Stores.SSM):
                if ParamStore.delete(key, store=ParamStore.Stores.SSM):
                    print('  - Key/Value has been deleted.')
                else:
                    print('  - Error deleting key/value.')
            else:
                print('  - Key does not exist.')

    print('')


def get_service_name():
    """
    Gets the service name from serverless.yml
    """
    yml = Config.open_local('serverless.yml')

    if isinstance(yml['service'], dict):
        return yml['service']['name']
    else:
        return yml['service']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--stage',
                        choices=Config.Stages.ALL,
                        help='The deploy stage.',
                        default=Config.Stages.DEVELOPMENT)
    parser.add_argument('-a', '--action',
                        choices=['import', 'delete'],
                        help='The action to take on the param store -- import or delete key values.',
                        default='import')
    args = parser.parse_args()

    service_stage = args.stage
    import_into_ssm(service_stage, args.action)


if __name__ == "__main__":
    main()
