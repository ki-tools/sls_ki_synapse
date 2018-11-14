import graphene
from .rally.queries import RallyQuery
from .rally.mutations import RallyMutation

class Query(
        RallyQuery,
        graphene.ObjectType):
    """
    Root Query Class.
    """
    pass


class Mutation(
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
