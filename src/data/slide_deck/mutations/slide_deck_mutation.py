import graphene
from .create_slide_deck import CreateSlideDeck


class SlideDeckMutation(graphene.ObjectType):
    """
    Defines all the SlideDeck mutations.
    """
    create_slide_deck = CreateSlideDeck.Field()
