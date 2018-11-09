import graphene
from .types import Rally
from core.synapse import Synapse
import kirallymanager.manager as krm


class RallyQuery(graphene.ObjectType):
    rally = graphene.Field(
        Rally, rallyAdminProjectId=graphene.String(), rallyNumber=graphene.Int())

    def resolve_rally(self, info, rallyAdminProjectId, rallyNumber):
        project = krm.getRally(
            Synapse.client(), rallyAdminProjectId, rallyNumber)
        if project:
            return Rally.from_project(project)
        else:
            return None
