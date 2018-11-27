import graphene
import json
from core import Synapse
from .post_data_input import PostDataInput
from .wiki_data_input import WikiDataInput
from ..types import SynProject
from synapseclient import Project, Folder, Team, Wiki


class CreateSynProject(graphene.Mutation):
    """
    Mutation for creating a SynProject.
    """
    ok = graphene.Boolean()
    syn_project = graphene.Field(lambda: SynProject)

    class Arguments:
        name = graphene.String(required=True)
        rallyAdminTeamId = graphene.Int(required=True)
        wiki = WikiDataInput()
        folders = graphene.List(graphene.String)
        posts = graphene.List(PostDataInput)

    def mutate(self,
               info,
               name,
               rallyAdminTeamId,
               wiki,
               folders,
               posts):

        # Create the Project
        project = Synapse.client().store(Project(name=name))

        # Add the admin team
        Synapse.client().setPermissions(
            project,
            rallyAdminTeamId,
            accessType=Synapse.ADMIN_PERMS,
            warn_if_inherits=False)

        # Add the the folders
        if folders:
            for folder_name in folders:
                Synapse.client().store(Folder(name=folder_name, parent=project))

        # Add the posts
        if posts:
            forum_id = Synapse.client().restGET(
                '/project/{0}/forum'.format(project.id)).get('id')
            for post in posts:
                body = {**post, **{'forumId': forum_id}}
                Synapse.client().restPOST("/thread", body=json.dumps(body))

        # Add the wiki
        if wiki:
            Synapse.client().store(Wiki(title=wiki.title, markdown=wiki.markdown, owner=project))

        new_syn_project = SynProject.from_project(project)

        is_ok = True
        return CreateSynProject(syn_project=new_syn_project, ok=is_ok)
