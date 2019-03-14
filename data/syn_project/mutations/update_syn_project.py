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
from ..types import SynProject
from .permission_data_input import PermissionDataInput


class UpdateSynProject(graphene.Mutation):
    """
    Mutation for updating a SynProject.
    """
    syn_project = graphene.Field(lambda: SynProject)

    class Arguments:
        id = graphene.String(required=True)
        name = graphene.String()
        permissions = graphene.List(PermissionDataInput)

    def mutate(self,
               info,
               id,
               name,
               permissions):

        # Create the Project
        project = Synapse.client().get(id)

        if name:
            project.name = name

        if permissions:
            for permission in permissions:
                principal_id = permission['principal_id']
                access = permission['access']
                access_type = getattr(Synapse, '{0}_PERMS'.format(access))

                # Only add permissions, do not update permissions.
                current_perms = Synapse.client().getPermissions(project, principal_id)
                
                if not current_perms:
                    Synapse.client().setPermissions(
                        project,
                        principal_id,
                        accessType=access_type,
                        warn_if_inherits=False
                    )
            # Remove permissions
            new_principal_ids = [int(p['principal_id']) for p in permissions]

            acl = Synapse.client()._getACL(project)

            current_principal_ids = [int(r['principalId'])
                                     for r in acl['resourceAccess']]

            for current_principal_id in current_principal_ids:
                if current_principal_id == int(project.createdBy):
                    continue
                    
                if current_principal_id not in new_principal_ids:
                    Synapse.client().setPermissions(project, current_principal_id,
                                                    accessType=None, warn_if_inherits=False)

        project = Synapse.client().store(project)
        updated_syn_project = SynProject.from_project(project)

        return UpdateSynProject(syn_project=updated_syn_project)
