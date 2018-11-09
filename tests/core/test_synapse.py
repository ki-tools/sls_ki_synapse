import pytest
from core.synapse import Synapse
from core.param_store import ParamStore

def test_client():
    assert Synapse.client() != None
    profile = Synapse.client().getUserProfile(refresh=True)
    assert profile['userName'] == ParamStore.SYNAPSE_USERNAME()
    