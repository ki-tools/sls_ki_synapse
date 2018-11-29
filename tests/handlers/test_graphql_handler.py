import pytest
from handlers import graphql_handler
from synapseclient import EntityViewSchema
import time
import json
from core import (ParamStore, Synapse)
from data.syn_project import (SynProject, SynProjectQuery)
from data.rally import (Rally, RallySprint, RallyQuery)


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
# Rally
###################################################################################################


def test_handler_get_rally(mocker):
    q = """
        query GetRally($rallyAdminProjectId: String!, $rallyNumber: Int!) {
            rally(rallyAdminProjectId: $rallyAdminProjectId, rallyNumber: $rallyNumber) {
                synId
            }
        }
    """
    v = {
        'rallyAdminProjectId': '1',
        'rallyNumber': 1
    }

    expected_syn_id = 'syn000'

    mock = mocker.patch.object(RallyQuery, 'resolve_rally')
    mock.return_value = Rally(synId=expected_syn_id)

    body = do_post(q, v).get('body')
    assert not body.get('errors', None)
    assert body['data']['rally']['synId'] == expected_syn_id


def test_query_rally(rally_setup, rally):
    q = """
        query GetRally($rallyAdminProjectId: String!, $rallyNumber: Int!) {
            rally(rallyAdminProjectId: $rallyAdminProjectId, rallyNumber: $rallyNumber) {
                synId
                number
                title
            }
        }
    """
    v = {
        'rallyAdminProjectId': rally_setup['rally_admin_project'].id,
        'rallyNumber': rally.number
    }

    body = do_post(q, v).get('body')
    assert not body.get('errors', None)
    assert body['data']['rally'] != None
    assert body['data']['rally']['synId'] == rally.synId
    assert body['data']['rally']['number'] == rally.number


def test_create_rally(rally_setup, rally_number, syn_client, syn_test_helper_session):
    rallyNumber = rally_number
    consortium = rally_setup['rally_config']['consortium']
    rallyAdminProjectId = rally_setup['rally_admin_project'].id
    wikiTaskTemplateId = rally_setup['master_task_wiki_template'].id
    wikiRallyTemplateId = rally_setup['master_rally_wiki_template'].id
    allFilesSchemaId = rally_setup['all_files_schema'].id
    defaultRallyTeamMembers = rally_setup['rally_config']['defaultRallyTeamMembers']
    rallyAdminTeamPermissions = rally_setup['rally_config']['rallyAdminTeamPermissions']

    q = '''
      mutation CreateRally($rallyNumber: Int!, $consortium: String!, $rallyAdminProjectId: String!, $wikiTaskTemplateId: String!, $wikiRallyTemplateId: String!, $allFilesSchemaId: String!, $defaultRallyTeamMembers: [Int]!, $rallyAdminTeamPermissions: [String]!) {
        createRally(rallyNumber: $rallyNumber, consortium: $consortium, rallyAdminProjectId: $rallyAdminProjectId, wikiTaskTemplateId: $wikiTaskTemplateId, wikiRallyTemplateId: $wikiRallyTemplateId, allFilesSchemaId: $allFilesSchemaId, defaultRallyTeamMembers: $defaultRallyTeamMembers, rallyAdminTeamPermissions: $rallyAdminTeamPermissions) {
          rally {
            synId
            number
            title
          }
          ok
        }
      }
    '''
    v = {
        'rallyNumber': rallyNumber,
        'consortium': consortium,
        'rallyAdminProjectId': rallyAdminProjectId,
        'wikiTaskTemplateId': wikiTaskTemplateId,
        'wikiRallyTemplateId': wikiRallyTemplateId,
        'allFilesSchemaId': allFilesSchemaId,
        'defaultRallyTeamMembers': defaultRallyTeamMembers,
        'rallyAdminTeamPermissions': rallyAdminTeamPermissions
    }

    body = do_post(q, v).get('body')
    assert not body.get('errors', None)

    # Get the project and team so they can be deleted.
    rally_project = syn_client.get(
        body['data']['createRally']['rally']['synId'])
    syn_test_helper_session.dispose_of(rally_project)

    rally = Rally.from_project(rally_project)

    rally_team = syn_client.getTeam(rally.rallyTeamId)
    syn_test_helper_session.dispose_of(rally_team)


###################################################################################################
# RallySprint
###################################################################################################

def test_handler_get_rally_sprint(mocker):
    q = """
        query GetRallySprint($rallyAdminProjectId: String!, $rallyNumber: Int!, $sprintLetter: String!) { 
            rallySprint(rallyAdminProjectId: $rallyAdminProjectId, rallyNumber: $rallyNumber, sprintLetter: $sprintLetter) {
                synId
            }
        }
    """
    v = {
        'rallyAdminProjectId': '1',
        'rallyNumber': 1,
        'sprintLetter': 'A'
    }

    expected_syn_id = 'syn000'

    mock = mocker.patch.object(RallyQuery, 'resolve_rally_sprint')
    mock.return_value = RallySprint(synId=expected_syn_id)

    body = do_post(q, v).get('body')
    assert not body.get('errors', None)
    assert body['data']['rallySprint']['synId'] == expected_syn_id


def test_query_rally_sprint(rally_setup, rally_sprint):
    q = """
        query GetRallySprint($rallyAdminProjectId: String!, $rallyNumber: Int!, $sprintLetter: String!) { 
            rallySprint(rallyAdminProjectId: $rallyAdminProjectId, rallyNumber: $rallyNumber, sprintLetter: $sprintLetter) {
                synId
                letter
            }
        }
    """
    v = {
        'rallyAdminProjectId': rally_setup['rally_admin_project'].id,
        'rallyNumber': rally_sprint.rallyNumber,
        'sprintLetter': rally_sprint.letter
    }

    body = do_post(q, v).get('body')
    assert not body.get('errors', None)
    assert body['data']['rallySprint'] != None
    assert body['data']['rallySprint']['synId'] == rally_sprint.synId
    assert body['data']['rallySprint']['letter'] == rally_sprint.letter


def test_create_rally_sprint(rally_setup, rally, syn_client, syn_test_helper_session):
    rallyNumber = rally.number
    sprintLetter = 'A'
    consortium = rally_setup['rally_config']['consortium']
    rallyAdminProjectId = rally_setup['rally_admin_project'].id
    wikiTaskTemplateId = rally_setup['master_task_wiki_template'].id
    wikiRallyTemplateId = rally_setup['master_rally_wiki_template'].id
    allFilesSchemaId = rally_setup['all_files_schema'].id
    defaultRallyTeamMembers = rally_setup['rally_config']['defaultRallyTeamMembers']
    rallyAdminTeamPermissions = rally_setup['rally_config']['rallyAdminTeamPermissions']
    sprintFolders = rally_setup['rally_config']['sprintFolders']
    posts = rally_setup['rally_config']['posts']

    # Remove the 'forumId' from the posts.
    # This value gets added when another tests uses a fixture that creates a sprint
    # TODO: Find a better way to handle this.
    for post in posts:
        post.pop('forumId', None)

    q = '''
      mutation CreateRallySprint($rallyNumber: Int!, $sprintLetter: String!, $consortium: String!, $rallyAdminProjectId: String!, $wikiTaskTemplateId: String!, $wikiRallyTemplateId: String!, $allFilesSchemaId: String!, $defaultRallyTeamMembers: [Int]!, $rallyAdminTeamPermissions: [String]!, $sprintFolders: [String]!, $posts: [PostDataInput]!) {
        createRallySprint(rallyNumber: $rallyNumber, sprintLetter: $sprintLetter, consortium: $consortium, rallyAdminProjectId: $rallyAdminProjectId, wikiTaskTemplateId: $wikiTaskTemplateId, wikiRallyTemplateId: $wikiRallyTemplateId, allFilesSchemaId: $allFilesSchemaId, defaultRallyTeamMembers: $defaultRallyTeamMembers, rallyAdminTeamPermissions: $rallyAdminTeamPermissions, sprintFolders: $sprintFolders, posts: $posts) {
          rallySprint {
            synId
            letter
          }
          ok
        }
      }
    '''
    v = {
        'rallyNumber': rallyNumber,
        'sprintLetter': sprintLetter,
        'consortium': consortium,
        'rallyAdminProjectId': rallyAdminProjectId,
        'wikiTaskTemplateId': wikiTaskTemplateId,
        'wikiRallyTemplateId': wikiRallyTemplateId,
        'allFilesSchemaId': allFilesSchemaId,
        'defaultRallyTeamMembers': defaultRallyTeamMembers,
        'rallyAdminTeamPermissions': rallyAdminTeamPermissions,
        'sprintFolders': sprintFolders,
        'posts': posts
    }

    body = do_post(q, v).get('body')
    assert not body.get('errors', None)

    # Get the project and team so they can be deleted.
    rally_project_sprint = syn_client.get(
        body['data']['createRallySprint']['rallySprint']['synId'])
    syn_test_helper_session.dispose_of(rally_project_sprint)
