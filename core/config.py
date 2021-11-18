import os
import json
import yaml


class Config:
    class Stages:
        PRODUCTION = 'production'
        STAGING = 'staging'
        DEVELOPMENT = 'development'
        TEST = 'test'
        ALL = [PRODUCTION, STAGING, DEVELOPMENT, TEST]

    @classmethod
    def load_local_into_env(cls, filename, stage=None):
        """Loads and sets OS environment variables from a local config file.

        This should only be called when locally developing, running tests, or setting remote SSM key/values.
        In production or CI all variables must be set in the OS environment or SSM and not loaded from a file.

        Args:
            filename: The filename of the config file to open.
            stage: Which stage to load from the config file (if JSON config file).

        Returns:
            Dictionary of key/values.
        """
        env_vars = cls.open_local(filename, stage=stage, for_env=True)

        for key, value in env_vars.items():
            if value is None:
                print('Environment variable: {0} has no value and will not be set.'.format(key))
            else:
                if isinstance(value, bool):
                    value = str(value).lower()
                elif not isinstance(value, str):
                    value = str(value)
                os.environ[key] = value

        return env_vars

    @classmethod
    def open_local(cls, filename, stage=None, for_env=False):
        """Opens a local config file and parses it.

        Args:
            filename: The filename of the config file to open.
            stage: Which stage to load from the config file (if JSON config file).
            for_env: Set to True if loading a file to set ENV variables.

        Returns:
            Dict of environment variables.
        """
        module_dir = os.path.dirname(os.path.abspath(__file__))
        src_root_dir = os.path.abspath(os.path.join(module_dir, '..'))
        config_file_path = os.path.join(src_root_dir, filename)

        result = {}

        if os.path.isfile(config_file_path):
            print('Loading local configuration from: {0}'.format(config_file_path))

            if filename.endswith('.yml'):
                config = yaml.safe_load(cls._read_file(config_file_path))
            else:
                config = json.loads(cls._read_file(config_file_path)).get(stage)

            for key, value in config.items():
                parsed_value = value

                if str(value).startswith('$ref:'):
                    filename = value.replace('$ref:', '')
                    parsed_value = cls._read_file(filename)

                if for_env:
                    if isinstance(parsed_value, list):
                        if len(parsed_value) > 0:
                            if isinstance(parsed_value[0], dict):
                                parsed_value = json.dumps(parsed_value)
                            else:
                                parsed_value = ','.join(parsed_value)
                        else:
                            parsed_value = ''
                    elif isinstance(parsed_value, dict):
                        parsed_value = json.dumps(parsed_value)

                result[key] = parsed_value
        else:
            print('Configuration file not found at: {0}'.format(config_file_path))

        return result

    @classmethod
    def _read_file(cls, path):
        with open(path, mode='r') as f:
            return f.read()
