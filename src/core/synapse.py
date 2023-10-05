from .env import Env
import os
import tempfile
import synapseclient


class Synapse:
    _synapse_client = None

    ADMIN_PERMS = [
        'UPDATE',
        'DELETE',
        'CHANGE_PERMISSIONS',
        'CHANGE_SETTINGS',
        'CREATE',
        'DOWNLOAD',
        'READ',
        'MODERATE'
    ]

    CAN_EDIT_AND_DELETE_PERMS = [
        'DOWNLOAD',
        'UPDATE',
        'CREATE',
        'DELETE',
        'READ'
    ]

    CAN_EDIT_PERMS = [
        'DOWNLOAD',
        'UPDATE',
        'CREATE',
        'READ'
    ]

    CAN_DOWNLOAD_PERMS = [
        'DOWNLOAD',
        'READ'
    ]

    CAN_VIEW_PERMS = [
        'READ'
    ]

    @classmethod
    def client(cls):
        """
        Gets a logged in instance of the synapseclient.
        """
        if not cls._synapse_client:
            # Lambda can only write to /tmp so update the CACHE_ROOT_DIR.
            synapseclient.core.cache.CACHE_ROOT_DIR = os.path.join(tempfile.gettempdir(), 'synapseCache')

            # Multiprocessing is not supported on Lambda.
            synapseclient.core.config.single_threaded = True

            auth_token = Env.SYNAPSE_AUTH_TOKEN()
            cls._synapse_client = synapseclient.Synapse(skip_checks=True, silent=True)
            cls._synapse_client.login(authToken=auth_token, silent=True, forced=True)

        return cls._synapse_client
