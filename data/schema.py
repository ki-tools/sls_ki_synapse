import graphene
from .rally.types import Rally
from .rally.queries import RallyQuery
from .rally.mutations import RallyMutation


class Query(RallyQuery, graphene.ObjectType):
    pass


class Mutation(RallyMutation, graphene.ObjectType):
    pass


def root():
    """
    Gets the GraphQL schema for the application.
    """
    return graphene.Schema(query=Query, mutation=Mutation)
