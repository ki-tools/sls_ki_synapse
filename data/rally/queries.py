import graphene
from .types import (Rally, RallySprint)
from core.synapse import Synapse
import kirallymanager.manager as krm


class RallyQuery(graphene.ObjectType):
    """
    Defines all the Rally queries.
    """
    rally = graphene.Field(
        Rally,
        rallyAdminProjectId=graphene.String(),
        rallyNumber=graphene.Int()
    )

    rally_sprint = graphene.Field(
        RallySprint,
        rallyAdminProjectId=graphene.String(),
        rallyNumber=graphene.Int(),
        sprintLetter=graphene.String()
    )

    def resolve_rally(self, info, rallyAdminProjectId, rallyNumber):
        """
        Gets a Rally via the ki-rally-manager.
        """
        project = krm.getRally(
            Synapse.client(), rallyAdminProjectId, rallyNumber)
        if project:
            return Rally.from_project(project)
        else:
            return None

    def resolve_rally_sprint(self, info, rallyAdminProjectId, rallyNumber, sprintLetter):
        """
        Gets a RallySprint via the ki-rally-manager.
        """
        project = krm.getSprint(
            Synapse.client(), rallyAdminProjectId, rallyNumber, sprintLetter)
        if project:
            return RallySprint.from_project(project)
        else:
            return None
