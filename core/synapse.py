import os
import tempfile
import synapseclient
from .param_store import ParamStore


class Synapse:

    _synapse_client = None

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
