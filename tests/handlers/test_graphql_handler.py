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

import pytest
from handlers import graphql_handler
from synapseclient import EntityViewSchema
import time
import json
import responses
from core import (ParamStore, Synapse)
from data.syn_project import (SynProject, SynProjectQuery)
from data.slide_deck import (SlideDeck, CreateSlideDeck)


def do_post(query, variables):
    """
    Executes a query against the handler.
    """
    event = {'body': json.dumps({'query': query, 'variables': variables})}
    context = None
    response = graphql_handler.graphql(event, context)

    # Convert the body to a dict so testing is easier.
    response['body'] = json.loads(response['body'])

    return response

###################################################################################################
# SynProject
###################################################################################################


def test_handler_get_syn_project(mocker):
    q = """
        query GetSynProject($id: String!) {
            synProject(id: $id) {
                id
                name
            }
        }
    """
    v = {
        'id': '1'
    }

    expected_syn_id = 'syn000'

    mock = mocker.patch.object(SynProjectQuery, 'resolve_syn_project')
    mock.return_value = SynProject(id=expected_syn_id)

    body = do_post(q, v).get('body')
    assert not body.get('errors', None)
    assert body['data']['synProject']['id'] == expected_syn_id


def test_query_syn_project(syn_test_helper):
    project = syn_test_helper.create_project()

    q = """
        query GetSynProject($id: String!) {
            synProject(id: $id) {
                id
                name
            }
        }
    """
    v = {
        'id': project.id
    }

    body = do_post(q, v).get('body')
    assert not body.get('errors', None)
    assert body['data']['synProject'] != None
    assert body['data']['synProject']['id'] == project.id
    assert body['data']['synProject']['name'] == project.name


def test_create_syn_project(syn_client, syn_test_helper):
    name = syn_test_helper.uniq_name(prefix='Syn Project ')

    admin_team = syn_test_helper.create_team()
    permissions = [{"principalId": str(admin_team.id), "access": "ADMIN"}]

    annotations = [{"key": "rally", "value": "1"},
                   {"key": "sprint", "value": "A"}]
    wiki = {'title': 'Main Wiki', 'markdown': 'main wiki markdown'}
    folders = ['Folder1', 'Folder2']
    posts = [{"title": "test1", "messageMarkdown": "markdown1"},
             {"title": "test2", "messageMarkdown": "markdown2"}]

    q = '''
      mutation CreateSynProject($name: String!, $permissions: [PermissionDataInput], $annotations: [AnnotationDataInput], $wiki: WikiDataInput, $folders: [String], $posts: [PostDataInput]) {
        createSynProject(name: $name, permissions: $permissions, annotations: $annotations, wiki: $wiki, folders: $folders, posts: $posts) {
          synProject {
            id
            name
          }
          ok
        }
      }
    '''
    v = {
        "name": name,
        "permissions": permissions,
        "annotations": annotations,
        "wiki": wiki,
        "folders": folders,
        "posts": posts
    }

    body = do_post(q, v).get('body')
    assert not body.get('errors', None)

    jsyn_project = body['data']['createSynProject']['synProject']
    assert jsyn_project['name'] == name

    project = syn_client.get(jsyn_project['id'])
    syn_test_helper.dispose_of(project)

    assert project.name == name

    # Admin Team
    for permission in permissions:
        principal_id = permission['principalId']
        access = permission['access']
        access_type = getattr(Synapse, '{0}_PERMS'.format(access))

        perms = syn_client.getPermissions(project, principal_id)
        assert set(perms) == set(access_type)

    # Annotations
    for annotation in annotations:
        assert project.annotations[annotation['key']][0] == annotation['value']

    # Wiki
    main_wiki = syn_client.getWiki(project)
    assert main_wiki.title == wiki['title']
    assert main_wiki.markdown == wiki['markdown']

    # Folders
    project_folders = syn_client.getChildren(project, includeTypes=['folder'])
    for project_folder in project_folders:
        assert project_folder['name'] in folders

    # Posts
    project_forum = syn_client.restGET('/project/{0}/forum'.format(project.id))
    threads = syn_client.restGET(
        '/forum/{0}/threads?limit=10&offset=0&filter=NO_FILTER'.format(project_forum.get('id')))
    for thread in threads['results']:
        assert thread['title'] in [p['title'] for p in posts]


def test_update_syn_project(syn_client, syn_test_helper):
    project = syn_test_helper.create_project()
    team = syn_test_helper.create_team()

    id = project.id
    name = syn_test_helper.uniq_name(prefix='New Project Name ')
    permissions = [{"principalId": int(team.id), "access": "CAN_EDIT"}]

    other_test_user_id = ParamStore._get_from_os('SYNAPSE_OTHER_USER_ID')
    if other_test_user_id:
        permissions.append(
            {"principalId": int(other_test_user_id), "access": "CAN_EDIT"})
    else:
        print('WARNING: SYNAPSE_OTHER_USER_ID environment variable not set.')

    q = '''
      mutation UpdateSynProject($id: String!, $name: String, $permissions: [PermissionDataInput]) {
        updateSynProject(id: $id, name: $name, permissions: $permissions) {
          synProject {
            id
            name
          }
          ok
        }
      }
    '''
    v = {
        "id": id,
        "name": name,
        "permissions": permissions
    }

    body = do_post(q, v).get('body')
    assert not body.get('errors', None)
    jsyn_project = body['data']['updateSynProject']['synProject']
    assert jsyn_project['name'] == name

    # Reload the project
    project = syn_client.get(project)
    assert project.name == name

    # Permissions
    for permission in permissions:
        principal_id = permission['principalId']
        access = permission['access']
        access_type = getattr(Synapse, '{0}_PERMS'.format(access))

        perms = syn_client.getPermissions(project, principal_id)
        assert set(perms) == set(access_type)

    # Make sure permissions are removed
    removed_perm = permissions.pop()

    body = do_post(q, v).get('body')
    assert not body.get('errors', None)

    acl = Synapse.client()._getACL(project)

    current_principal_ids = [int(r['principalId'])
                             for r in acl['resourceAccess']]

    assert int(removed_perm['principalId']) not in current_principal_ids


###################################################################################################
# SlideDeck
###################################################################################################

def test_handler_create_slide_deck(mocker):
    q = """
        mutation CreateSlideDeck($synapseProjectId: String!, $title: String!, $presenter: String!, $sprintId: String!, $participants: [String]!, $endDate: String!, $sprintQuestions: [String]!, $background: String!, $problemStatement: String!, $motivation: String!, $deliverables: [String]!, $keyFindings: [String]!, $nextSteps: [String]!, $value: String!, $templateUrl: String) {
            createSlideDeck(synapseProjectId: $synapseProjectId, title: $title, presenter: $presenter, sprintId: $sprintId, participants: $participants, endDate: $endDate, sprintQuestions: $sprintQuestions, background: $background, problemStatement: $problemStatement, motivation: $motivation, deliverables: $deliverables, keyFindings: $keyFindings, nextSteps: $nextSteps, value: $value, templateUrl: $templateUrl) {
                slideDeck {
                    synapseId
                }
            }
        }
    """
    v = {
        'synapseProjectId': 'syn0',
        'title': 'My Title',
        'presenter': 'Name1',
        'sprintId': 'A',
        'participants': ['Name1', 'Name2', 'Name3'],
        'endDate': '2018-01-01',
        'sprintQuestions': ['Question1', 'Question2', 'Question3'],
        'background': 'Some Background Info',
        'problemStatement': 'Some Problems',
        'motivation': 'Some Motivation',
        'deliverables': ['Deliverable1', 'Deliverable2', 'Deliverable3'],
        'keyFindings': ['Finding1', 'Finding2', 'Finding3'],
        'nextSteps': ['Step1', 'Step2', 'Step3'],
        'value': 'Some Value',
        'templateUrl': None
    }

    expected_id = 'syn123'

    # TODO: Figure out why this mock is not working. It still calls the original method.
    #
    # mock = mocker.patch.object(CreateSlideDeck, 'mutate')
    # mock.return_value = SlideDeck(url=expected_url)

    # body = do_post(q, v).get('body')
    # assert not body.get('errors', None)
    # jslide_deck = body['data']['createSlideDeck']['slideDeck']
    # assert jslide_deck['synapseId'] == expected_id


@responses.activate
def test_create_slide_deck(syn_client, syn_test_helper):
    for url in [
        'https://repo-prod.prod.sagebase.org',
        'https://auth-prod.prod.sagebase.org',
        'https://file-prod.prod.sagebase.org',
        'https://www.synapse.org',
            'https://s3.amazonaws.com']:
        responses.add_passthru(url)

    project = syn_test_helper.create_project()

    q = """
        mutation CreateSlideDeck($synapseProjectId: String!, $title: String!, $presenter: String!, $sprintId: String!, $participants: [String]!, $endDate: String!, $sprintQuestions: [String]!, $background: String!, $problemStatement: String!, $motivation: String!, $deliverables: [String]!, $keyFindings: [String]!, $nextSteps: [String]!, $value: String!, $templateUrl: String) {
            createSlideDeck(synapseProjectId: $synapseProjectId, title: $title, presenter: $presenter, sprintId: $sprintId, participants: $participants, endDate: $endDate, sprintQuestions: $sprintQuestions, background: $background, problemStatement: $problemStatement, motivation: $motivation, deliverables: $deliverables, keyFindings: $keyFindings, nextSteps: $nextSteps, value: $value, templateUrl: $templateUrl) {
                slideDeck {
                    synapseId
                }
            }
        }
    """
    v = {
        'synapseProjectId': project.id,
        'title': 'My Title',
        'presenter': 'Name1',
        'sprintId': 'A',
        'participants': ['Name1', 'Name2', 'Name3'],
        'endDate': '2018-01-01',
        'sprintQuestions': ['Question1', 'Question2', 'Question3'],
        'background': 'Some Background Info',
        'problemStatement': 'Some Problems',
        'motivation': 'Some Motivation',
        'deliverables': ['Deliverable1', 'Deliverable2', 'Deliverable3'],
        'keyFindings': ['Finding1', 'Finding2', 'Finding3'],
        'nextSteps': ['Step1', 'Step2', 'Step3'],
        'value': 'Some Value'
    }

    body = do_post(q, v).get('body')
    assert not body.get('errors', None)
    jslide_deck = body['data']['createSlideDeck']['slideDeck']
    assert jslide_deck['synapseId'] != None
    file = syn_client.get(jslide_deck['synapseId'], downloadFile=False)
    assert file != None

    # Updates the file
    body = do_post(q, v).get('body')
    assert not body.get('errors', None)
    jslide_deck = body['data']['createSlideDeck']['slideDeck']
    file_v2 = syn_client.get(jslide_deck['synapseId'], downloadFile=False)
    assert file_v2.versionNumber > file.versionNumber

    # Uses the template_url
    template_url = 'https://afakedomainname.com/file.pptx'
    v['templateUrl'] = template_url

    pptx = None
    with open('assets/template_ki_empty.pptx', 'rb') as f:
        pptx = f.read()

    responses.add(responses.GET, template_url, body=pptx, status=200)

    body = do_post(q, v).get('body')
    assert not body.get('errors', None)
