from sls_tools.param_store import ParamStore


class Env:
    @staticmethod
    def SERVICE_NAME(default=None):
        """
        This variable must be set on the OS (not on SSM)
        """
        return ParamStore.get('SERVICE_NAME', default=default, store=ParamStore.Stores.OS).value

    @staticmethod
    def SERVICE_STAGE(default=None):
        """
        This variable must be set on the OS (not on SSM)
        """
        return ParamStore.get('SERVICE_STAGE', default=default, store=ParamStore.Stores.OS).value

    @staticmethod
    def LOG_LEVEL(default=None):
        return ParamStore.get('LOG_LEVEL', default=default).value

    @staticmethod
    def SYNAPSE_USERNAME(default=None):
        return ParamStore.get('SYNAPSE_USERNAME', default=default).value

    @staticmethod
    def SYNAPSE_PASSWORD(default=None):
        return ParamStore.get('SYNAPSE_PASSWORD', default=default).value

    @staticmethod
    def JWT_SECRET(default=None):
        """
        Secret key used to encode JWTs.
        """
        return ParamStore.get('JWT_SECRET', default=default).value

    @staticmethod
    def JWT_API_KEYS(default=None):
        """
        String of comma separated keys that are used for API access.

        Returns:
            List of strings.
        """
        return ParamStore.get('JWT_API_KEYS', default=default).to_list(delimiter=',')

    @staticmethod
    def SLIDE_DECKS_BUCKET_NAME(default=None):
        return ParamStore.get('SLIDE_DECKS_BUCKET_NAME', default=default).value

    @staticmethod
    def SLIDE_DECKS_URL_EXPIRES_IN_SECONDS(default=300):
        return ParamStore.get('SLIDE_DECKS_URL_EXPIRES_IN_SECONDS', default=default).to_int()
