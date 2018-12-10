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
from .syn_project import (SynProjectQuery, SynProjectMutation)
from .slide_deck import SlideDeckMutation


class Query(
        SynProjectQuery,
        graphene.ObjectType):
    """
    Root Query Class.
    """
    pass


class Mutation(
        SynProjectMutation,
        SlideDeckMutation,
        graphene.ObjectType):
    """
    Root Mutation Class.
    """
    pass


def root():
    """
    Gets the GraphQL schema for the application.
    """
    return graphene.Schema(query=Query, mutation=Mutation)
