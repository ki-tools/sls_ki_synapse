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


class RallySprint(graphene.ObjectType):
    """
    Defines the RallySprint type.
    """
    synId = graphene.String()
    letter = graphene.String()
    title = graphene.String()
    rallySynId = graphene.String()
    rallyNumber = graphene.Int()

    @staticmethod
    def from_project(project):
        """
        Converts a Project to a RallySprint.
        """
        return RallySprint(
            synId=project.id,
            letter=project.annotations.sprintLetter[0],
            title=project.name,
            rallySynId=project.annotations.rallyId[0],
            rallyNumber=project.annotations.rally[0]
        )
