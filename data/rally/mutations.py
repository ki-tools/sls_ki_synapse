import graphene
from .types import Rally
from core.synapse import Synapse
import kirallymanager.manager as krm


class PostDataInput(graphene.InputObjectType):
    title = graphene.String(required=True)
    messageMarkdown = graphene.String()


class CreateRally(graphene.Mutation):
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
        sprintFolders = graphene.List(graphene.String)
        posts = graphene.List(PostDataInput)

    def mutate(self, info,
               rallyNumber,
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

        project = krm.createRally(Synapse.client(), rallyNumber, rally_config)

        new_rally = Rally.from_project(project)

        is_ok = True
        return CreateRally(rally=new_rally, ok=is_ok)


class RallyMutation(graphene.ObjectType):
    create_rally = CreateRally.Field()
