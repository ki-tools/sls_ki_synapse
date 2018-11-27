import graphene
from core import Synapse
from ..types import Rally
import kirallymanager.manager as krm


class CreateRally(graphene.Mutation):
    """
    Mutation for creating a Rally.
    """
    ok = graphene.Boolean()
    rally = graphene.Field(lambda: Rally)

    class Arguments:
        rallyNumber = graphene.Int(required=True)
        consortium = graphene.String()
        rallyAdminProjectId = graphene.String(required=True)
        wikiTaskTemplateId = graphene.String(required=True)
        wikiRallyTemplateId = graphene.String(required=True)
        allFilesSchemaId = graphene.String(required=True)
        defaultRallyTeamMembers = graphene.List(graphene.Int)
        rallyAdminTeamPermissions = graphene.List(
            graphene.String, required=True)

    def mutate(self,
               info,
               rallyNumber,
               consortium,
               rallyAdminProjectId,
               wikiTaskTemplateId,
               wikiRallyTemplateId,
               allFilesSchemaId,
               defaultRallyTeamMembers,
               rallyAdminTeamPermissions):

        rally_config = {
            "consortium": consortium,
            "rallyAdminProjectId": rallyAdminProjectId,
            "wikiTaskTemplateId": wikiTaskTemplateId,
            "wikiRallyTemplateId": wikiRallyTemplateId,
            "allFilesSchemaId": allFilesSchemaId,
            "defaultRallyTeamMembers": defaultRallyTeamMembers,
            "rallyAdminTeamPermissions": rallyAdminTeamPermissions
        }

        project = krm.createRally(Synapse.client(), rallyNumber, rally_config)

        new_rally = Rally.from_project(project)

        is_ok = True
        return CreateRally(rally=new_rally, ok=is_ok)
