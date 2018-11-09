import os
import boto3
import logging


class ParamStore:

    @classmethod
    def get(cls, key, default=None):
        """
        Tries to get a value from the OS then SSM otherwise it returns the default value.
        """
        # Try to get the value from the local environment.
        result = cls._get_from_os(key)
        if result != None:
            return result

        # Try to get the value from SSM.
        result = cls._get_from_ssm(key)
        if result != None:
            return result

        return default

    @classmethod
    def _get_from_os(cls, key):
        """
        Gets a value from the OS.
        """
        return os.environ.get(key)

    @classmethod
    def _get_from_ssm(cls, key):
        """
        Gets a value from SSM.
        """
        client = boto3.client('ssm')
        ssm_key = cls._build_ssm_key(key)
        result = None

        try:
            get_response = client.get_parameter(Name=ssm_key, WithDecryption=True)
            result = get_response.get('Parameter').get('Value')
        except client.exceptions.ParameterNotFound:
            logging.exception('SSM Parameter Not Found: {}'.format(ssm_key))

        return result

    @classmethod
    def _set_ssm_parameter(cls, key, value, type='string'):
        """
        Sets an SSM key/value.
        """
        client = boto3.client('ssm')
        ssm_key = cls._build_ssm_key(key)
        return client.put_parameter(Name=ssm_key, Value=value, Type=type)

    @classmethod
    def _build_ssm_key(cls, key):
        """
        Builds a SSM key in the format for service_name/service_stage/key.
        """
        return '{0}/{1}/{2}'.format(os.environ.get('SERVICE_NAME'), os.environ.get('SERVICE_STAGE'), key)

    """
    ===============================================================================================
    Getter Methods.
    ===============================================================================================
    """

    @classmethod
    def SERVICE_NAME(cls, default=None):
        return cls.get('SERVICE_NAME', default)

    @classmethod
    def SERVICE_STAGE(cls, default=None):
        return cls.get('SERVICE_STAGE', default)

    @classmethod
    def LOG_LEVEL(cls, default=None):
        return cls.get('LOG_LEVEL', default)

    @classmethod
    def SQS_DISPATCH_QUEUE_URL(cls, default=None):
        return cls.get('SQS_DISPATCH_QUEUE_URL', default)

    @classmethod
    def SYNAPSE_API_KEY(cls, default=None):
        return cls.get('SYNAPSE_API_KEY', default)

    @classmethod
    def SYNAPSE_USERNAME(cls, default=None):
        return cls.get('SYNAPSE_USERNAME', default)

    @classmethod
    def SYNAPSE_PASSWORD(cls, default=None):
        return cls.get('SYNAPSE_PASSWORD', default)
