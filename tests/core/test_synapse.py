from src.core import Synapse


def test_client():
    assert Synapse.client() is not None
    profile = Synapse.client().getUserProfile(refresh=True)
    assert profile['userName']
