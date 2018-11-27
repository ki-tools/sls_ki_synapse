import graphene
from .syn_project import (SynProjectQuery, SynProjectMutation)
from .rally import (RallyQuery, RallyMutation)


class Query(
        SynProjectQuery,
        RallyQuery,
        graphene.ObjectType):
    """
    Root Query Class.
    """
    pass


class Mutation(
        SynProjectMutation,
        RallyMutation,
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
