import pytest
from core import Env, Synapse


def test_client():
    assert Synapse.client() is not None
    profile = Synapse.client().getUserProfile(refresh=True)
    assert profile['userName'] == Env.SYNAPSE_USERNAME()
