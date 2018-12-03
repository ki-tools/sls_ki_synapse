# Copyright 2018-present, Bill & Melinda Gates Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from .param_store import ParamStore
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
            synapseclient.cache.CACHE_ROOT_DIR = os.path.join(
                tempfile.gettempdir(), 'synapseCache')

            # TODO: Remove when this is fixed: https://sagebionetworks.jira.com/browse/SYNPY-855
            synapseclient.config.single_threaded = True

            syn_user = ParamStore.SYNAPSE_USERNAME()
            syn_pass = ParamStore.SYNAPSE_PASSWORD()
            cls._synapse_client = synapseclient.Synapse()
            cls._synapse_client.login(syn_user, syn_pass, silent=True)

        return cls._synapse_client
