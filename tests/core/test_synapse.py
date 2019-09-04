import pytest
from core import AppEnv, Synapse


def test_client():
    assert Synapse.client() is not None
    profile = Synapse.client().getUserProfile(refresh=True)
    assert profile['userName'] == AppEnv.SYNAPSE_USERNAME()
