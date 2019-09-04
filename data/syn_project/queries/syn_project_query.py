import graphene
from ..types import SynProject
from core import Synapse


class SynProjectQuery(graphene.ObjectType):
    """
    Defines all the SynProject queries.
    """
    syn_project = graphene.Field(
        SynProject,
        id=graphene.String(required=True)
    )

    def resolve_syn_project(self, info, id):
        project = Synapse.client().get(id)
        if project:
            return SynProject.from_project(project)
        else:
            return None
