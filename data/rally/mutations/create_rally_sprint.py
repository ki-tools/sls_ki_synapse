import graphene
from ..types import RallySprint
from core import Synapse
from data.syn_project import PostDataInput
import kirallymanager.manager as krm


class CreateRallySprint(graphene.Mutation):
    """
    Mutation for creating a Rally Sprint.
    """
    ok = graphene.Boolean()
    rally_sprint = graphene.Field(lambda: RallySprint)

    class Arguments:
        rallyNumber = graphene.Int(required=True)
        sprintLetter = graphene.String(required=True)
        consortium = graphene.String()
        rallyAdminProjectId = graphene.String(required=True)
        wikiTaskTemplateId = graphene.String(required=True)
        wikiRallyTemplateId = graphene.String(required=True)
        allFilesSchemaId = graphene.String(required=True)
        defaultRallyTeamMembers = graphene.List(graphene.Int)
        rallyAdminTeamPermissions = graphene.List(
            graphene.String, required=True)
        sprintFolders = graphene.List(graphene.String)
        posts = graphene.List(PostDataInput)

    def mutate(self,
               info,
               rallyNumber,
               sprintLetter,
               consortium,
               rallyAdminProjectId,
               wikiTaskTemplateId,
               wikiRallyTemplateId,
               allFilesSchemaId,
               defaultRallyTeamMembers,
               rallyAdminTeamPermissions,
               sprintFolders,
               posts):

        rally_config = {
            "consortium": consortium,
            "rallyAdminProjectId": rallyAdminProjectId,
            "wikiTaskTemplateId": wikiTaskTemplateId,
            "wikiRallyTemplateId": wikiRallyTemplateId,
            "allFilesSchemaId": allFilesSchemaId,
            "defaultRallyTeamMembers": defaultRallyTeamMembers,
            "rallyAdminTeamPermissions": rallyAdminTeamPermissions,
            "sprintFolders": sprintFolders,
            "posts": []
        }
        for post in posts:
            rally_config['posts'].append({
                "title": post.title,
                "messageMarkdown": post.messageMarkdown
            })

        project = krm.createSprint(
            Synapse.client(), rallyNumber, sprintLetter, rally_config)

        new_rally_sprint = RallySprint.from_project(project)

        is_ok = True
        return CreateRallySprint(rally_sprint=new_rally_sprint, ok=is_ok)
