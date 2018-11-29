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


class SynapseAccessType(graphene.Enum):
    """
    Synapse permissions.
    """
    ADMIN = 'ADMIN'
    CAN_EDIT_AND_DELETE = 'CAN_EDIT_AND_DELETE'
    CAN_EDIT = 'CAN_EDIT'
    CAN_DOWNLOAD = 'CAN_DOWNLOAD'
    CAN_VIEW = 'CAN_VIEW'


class PermissionDataInput(graphene.InputObjectType):
    """
    Input class for 'permissions' data.
    """
    principal_id = graphene.Int(
        required=True, description='ID of a Synapse user or team.')
    access = graphene.Field(SynapseAccessType, required=True)
