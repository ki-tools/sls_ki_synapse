import graphene


class SlideDeck(graphene.ObjectType):
    """
    Defines the SlideDeck type.
    """
    url = graphene.String()
