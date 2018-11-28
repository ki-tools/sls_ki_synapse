import os
import tempfile
import synapseclient
from .param_store import ParamStore


class Synapse:

    _synapse_client = None

    ADMIN_PERMS = ['UPDATE','DELETE','CHANGE_PERMISSIONS','CHANGE_SETTINGS','CREATE','DOWNLOAD','READ','MODERATE']
    CAN_EDIT_AND_DELETE_PERMS = ['DOWNLOAD','UPDATE','CREATE','DELETE','READ']
    CAN_EDIT_PERMS = ['DOWNLOAD','UPDATE','CREATE','READ']
    CAN_DOWNLOAD_PERMS = ['DOWNLOAD', 'READ']
    CAN_VIEW_PERMS = ['READ']

    @classmethod
    def client(cls):

        """
        Gets a logged in instance of the synapseclient.
        """
        if not cls._synapse_client:
            # Lambda can only write to /tmp so update the CACHE_ROOT_DIR.
            synapseclient.cache.CACHE_ROOT_DIR = os.path.join(
                tempfile.gettempdir(), 'synapseCache')

            syn_user = ParamStore.SYNAPSE_USERNAME()
            syn_pass = ParamStore.SYNAPSE_PASSWORD()
            cls._synapse_client = synapseclient.Synapse()
            cls._synapse_client.login(syn_user, syn_pass, silent=True)
        return cls._synapse_client
