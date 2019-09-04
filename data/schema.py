import graphene
from .syn_project import (SynProjectQuery, SynProjectMutation)
from .slide_deck import SlideDeckMutation


class Query(
    SynProjectQuery,
    graphene.ObjectType):
    """
    Root Query Class.
    """
    pass


class Mutation(
    SynProjectMutation,
    SlideDeckMutation,
    graphene.ObjectType):
    """
    Root Mutation Class.
    """
    pass


def root():
    """
    Gets the GraphQL schema for the application.
    """
    return graphene.Schema(query=Query, mutation=Mutation)
