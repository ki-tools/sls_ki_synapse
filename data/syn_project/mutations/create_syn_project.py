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
from core.log import logger
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
    errors = graphene.List(graphene.String)

    class Arguments:
        name = graphene.String(required=True)
        permissions = graphene.List(PermissionDataInput)
        annotations = graphene.List(AnnotationDataInput)
        wiki = WikiDataInput()
        folders = graphene.List(graphene.String)
        posts = graphene.List(PostDataInput)

    def mutate(self, info, name, **kwargs):
        errors = []

        permissions = kwargs.get('permissions', None)
        annotations = kwargs.get('annotations', None)
        wiki = kwargs.get('wiki', None)
        folders = kwargs.get('folders', None)
        posts = kwargs.get('posts', None)

        # Check if a project with the same name already exists.
        project_name_taken = Synapse.client().findEntityId(name) is not None

        if project_name_taken:
            raise ValueError('Another Synapse project with the name: {0} already exists.'.format(name))

        # Build the annotations
        project_annotations = {}
        if annotations:
            for annotation in annotations:
                project_annotations[annotation['key']] = annotation['value']

        # Create the Project
        project = Synapse.client().store(Project(name=name, annotations=project_annotations))

        # Add the permissions
        if permissions:
            for permission in permissions:
                try:
                    principal_id = permission.get('principal_id')
                    access = permission.get('access')
                    access_type = getattr(Synapse, '{0}_PERMS'.format(access))

                    try:
                        Synapse.client().setPermissions(project,
                                                        principal_id,
                                                        accessType=access_type,
                                                        warn_if_inherits=False)
                    except Exception as syn_ex:
                        logger.exception('Error setting permission: {0} - {1}'.format(permission, syn_ex))
                        if 'a foreign key constraint fails' in str(syn_ex):
                            errors.append('User or Team ID: {0} does not exist.'.format(principal_id))
                        else:
                            errors.append('Error setting permission for User or Team ID: {0}'.format(principal_id))

                except Exception as ex:
                    logger.exception('Error creating project permissions: {0} - {1}'.format(permission, ex))
                    errors.append('Error creating project permissions.')

        # Add the the folders
        if folders:
            for folder_name in folders:
                try:
                    Synapse.client().store(Folder(name=folder_name, parent=project))
                except Exception as syn_ex:
                    logger.exception('Error creating project folder: {0} - {1}'.format(folder_name, syn_ex))
                    errors.append('Error creating project folder: {0}.'.format(folder_name))

        # Add the posts
        if posts:
            try:
                forum_id = Synapse.client().restGET('/project/{0}/forum'.format(project.id)).get('id')

                for post in posts:
                    try:
                        body = {
                            'forumId': forum_id,
                            'title': post.get('title'),
                            'messageMarkdown': post.get('message_markdown')
                        }
                        Synapse.client().restPOST('/thread', body=json.dumps(body))
                    except Exception as syn_ex:
                        logger.exception('Error creating project post: {0} - {1}'.format(post, syn_ex))
                        errors.append('Error creating project post: {0}.'.format(post.get('title', None)))

            except Exception as ex:
                logger.exception('Error creating project posts: {1} - {0}'.format(posts, ex))
                errors.append('Error creating projects posts.')

        # Add the wiki
        if wiki:
            try:
                Synapse.client().store(Wiki(title=wiki.title, markdown=wiki.markdown, owner=project))
            except Exception as syn_ex:
                logger.exception('Error creating project wiki: {0} - {1}'.format(wiki, syn_ex))
                errors.append('Error creating project wiki.')

        new_syn_project = SynProject.from_project(project)

        return CreateSynProject(syn_project=new_syn_project, errors=(errors if errors else None))
