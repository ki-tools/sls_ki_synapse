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
from ..types import (Rally, RallySprint)
from core import Synapse
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
