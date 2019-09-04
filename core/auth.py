from .app_env import AppEnv
import jwt


class Auth:
    """
    Provides basic JWT authentication for the service.
    """

    @classmethod
    def authenticate(cls, token):
        secret = AppEnv.JWT_SECRET()
        api_keys = AppEnv.JWT_API_KEYS()
        payload = cls.decode_jwt(token, secret)
        api_key = payload['apiKey']

        if api_key in api_keys:
            return api_key
        else:
            return None

    @classmethod
    def decode_jwt(cls, token, secret):
        return jwt.decode(token, key=secret, algorithms=['HS256'])

    @classmethod
    def encode_jwt(cls, secret, api_key):
        return jwt.encode({'apiKey': api_key}, secret, algorithm='HS256').decode()
