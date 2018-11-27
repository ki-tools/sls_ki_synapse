import pytest
from core import (ParamStore, Synapse)


def test_client():
    assert Synapse.client() != None
    profile = Synapse.client().getUserProfile(refresh=True)
    assert profile['userName'] == ParamStore.SYNAPSE_USERNAME()
    