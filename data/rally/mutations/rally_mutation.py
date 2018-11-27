import graphene
from .create_rally import CreateRally
from .create_rally_sprint import CreateRallySprint


class RallyMutation(graphene.ObjectType):
    """
    Defines all the Rally mutations.
    """
    create_rally = CreateRally.Field()
    create_rally_sprint = CreateRallySprint.Field()
