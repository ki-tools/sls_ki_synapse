from sls_tools.param_store import ParamStore


class Env:
    @classmethod
    def SERVICE_NAME(cls, default=None):
        """
        This variable must be set on the OS (not on SSM)
        """
        return ParamStore.get('SERVICE_NAME', default=default, store=ParamStore.Stores.OS).value

    @classmethod
    def SERVICE_STAGE(cls, default=None):
        """
        This variable must be set on the OS (not on SSM)
        """
        return ParamStore.get('SERVICE_STAGE', default=default, store=ParamStore.Stores.OS).value

    @classmethod
    def LOG_LEVEL(cls, default=None):
        return ParamStore.get('LOG_LEVEL', default=default).value

    @classmethod
    def SYNAPSE_USERNAME(cls, default=None):
        return ParamStore.get('SYNAPSE_USERNAME', default=default).value

    @classmethod
    def SYNAPSE_PASSWORD(cls, default=None):
        return ParamStore.get('SYNAPSE_PASSWORD', default=default).value

    @classmethod
    def JWT_SECRET(cls, default=None):
        """
        Secret key used to encode JWTs.
        """
        return ParamStore.get('JWT_SECRET', default=default).value

    @classmethod
    def JWT_API_KEYS(cls, default=None):
        """
        String of comma separated keys that are used for API access.

        Returns:
            List of strings.
        """
        return ParamStore.get('JWT_API_KEYS', default=default).to_list(delimiter=',')

    @classmethod
    def SLIDE_DECKS_BUCKET_NAME(cls, default=None):
        return ParamStore.get('SLIDE_DECKS_BUCKET_NAME', default=default).value

    @classmethod
    def SLIDE_DECKS_URL_EXPIRES_IN_SECONDS(cls, default=300):
        return ParamStore.get('SLIDE_DECKS_URL_EXPIRES_IN_SECONDS', default=default).to_int()
