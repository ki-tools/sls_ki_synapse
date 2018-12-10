# Copyright 2018-present, Bill & Melinda Gates Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import graphene
import json
from core import Synapse
from .annotation_data_input import AnnotationDataInput
from .permission_data_input import PermissionDataInput
from .post_data_input import PostDataInput
from .wiki_data_input import WikiDataInput
from ..types import SynProject
from synapseclient import Project, Folder, Team, Wiki


class CreateSynProject(graphene.Mutation):
    """
    Mutation for creating a SynProject.
    """
    syn_project = graphene.Field(lambda: SynProject)

    class Arguments:
        name = graphene.String(required=True)
        permissions = graphene.List(PermissionDataInput)
        annotations = graphene.List(AnnotationDataInput)
        wiki = WikiDataInput()
        folders = graphene.List(graphene.String)
        posts = graphene.List(PostDataInput)

    def mutate(self,
               info,
               name,
               permissions,
               annotations,
               wiki,
               folders,
               posts):

        # Build the annotations
        project_annotations = {}
        if annotations:
            for annotation in annotations:
                project_annotations[annotation['key']] = annotation['value']

        # Create the Project
        project = Synapse.client().store(
            Project(name=name, annotations=project_annotations)
        )

        # Add the permissions
        if permissions:
            for permission in permissions:
                principal_id = permission['principal_id']
                access = permission['access']
                access_type = getattr(Synapse, '{0}_PERMS'.format(access))

                Synapse.client().setPermissions(
                    project,
                    principal_id,
                    accessType=access_type,
                    warn_if_inherits=False
                )

        # Add the the folders
        if folders:
            for folder_name in folders:
                Synapse.client().store(Folder(name=folder_name, parent=project))

        # Add the posts
        if posts:
            forum_id = Synapse.client().restGET(
                '/project/{0}/forum'.format(project.id)).get('id')
            for post in posts:
                #body = {**post, **{'forumId': forum_id}}
                body = {
                    'forumId': forum_id,
                    'title': post['title'],
                    'messageMarkdown': post['message_markdown']
                }
                Synapse.client().restPOST("/thread", body=json.dumps(body))

        # Add the wiki
        if wiki:
            Synapse.client().store(Wiki(title=wiki.title, markdown=wiki.markdown, owner=project))

        new_syn_project = SynProject.from_project(project)

        return CreateSynProject(syn_project=new_syn_project)
