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
                "messageMarkdown": post.message_markdown
            })

        project = krm.createSprint(
            Synapse.client(), rallyNumber, sprintLetter, rally_config)

        new_rally_sprint = RallySprint.from_project(project)

        is_ok = True
        return CreateRallySprint(rally_sprint=new_rally_sprint, ok=is_ok)
