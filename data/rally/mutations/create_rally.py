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
