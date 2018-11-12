import pytest
from handlers import handler
from synapseclient import EntityViewSchema, Schema, Column, Table, Row, RowSet
import time
from data.rally.types import Rally
from data.rally.queries import RallyQuery


def test_handler(mocker):
    q = """
        query GetRally($rallyAdminProjectId: String!, $rallyNumber: Int!) {
            rally(rallyAdminProjectId: $rallyAdminProjectId, rallyNumber: $rallyNumber) {
                synId
            }
        }
    """
    v = {
        'rallyAdminProjectId': '1',
        'rallyNumber': 9
    }

    mock = mocker.patch.object(RallyQuery, 'resolve_rally')
    mock.return_value = Rally()

    resp = handler.graphql({'query': q, 'variables': v}, None)
    assert not resp.get('errors', None)


def test_query_rally(rally_setup, rally_project):
    rally = Rally.from_project(rally_project)

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

    resp = handler.graphql({'query': q, 'variables': v}, None)
    assert not resp.get('errors', None)
    assert resp['data']['rally'] != None
    assert resp['data']['rally']['synId'] == rally.synId


def test_create_rally(rally_setup, rally_number, syn_client, syn_test_helper_session):
    rallyNumber = rally_number
    consortium = rally_setup['rally_config']['consortium']
    rallyAdminProjectId = rally_setup['rally_admin_project'].id
    wikiTaskTemplateId = rally_setup['master_task_wiki_template'].id
    wikiRallyTemplateId = rally_setup['master_rally_wiki_template'].id
    allFilesSchemaId = rally_setup['all_files_schema'].id
    defaultRallyTeamMembers = rally_setup['rally_config']['defaultRallyTeamMembers']
    rallyAdminTeamPermissions = rally_setup['rally_config']['rallyAdminTeamPermissions']
    sprintFolders = rally_setup['rally_config']['sprintFolders']
    posts = rally_setup['rally_config']['posts']

    q = '''
       mutation CreateNewRally($rallyNumber: Int!, $consortium: String!, $rallyAdminProjectId: String!, $wikiTaskTemplateId: String!, $wikiRallyTemplateId: String!, $allFilesSchemaId: String!, $defaultRallyTeamMembers: [Int]!, $rallyAdminTeamPermissions: [String]!, $sprintFolders: [String]!, $posts: [PostDataInput]!) {
        createRally(rallyNumber: $rallyNumber, consortium: $consortium, rallyAdminProjectId: $rallyAdminProjectId, wikiTaskTemplateId: $wikiTaskTemplateId, wikiRallyTemplateId: $wikiRallyTemplateId, allFilesSchemaId: $allFilesSchemaId, defaultRallyTeamMembers: $defaultRallyTeamMembers, rallyAdminTeamPermissions: $rallyAdminTeamPermissions, sprintFolders: $sprintFolders, posts: $posts) {
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
        'rallyAdminTeamPermissions': rallyAdminTeamPermissions,
        'sprintFolders': sprintFolders,
        'posts': posts
    }

    resp = handler.graphql({'query': q, 'variables': v}, None)
    assert not resp.get('errors', None)

    # Get the project and team so they can be deleted.
    rally_project = syn_client.get(
        resp['data']['createRally']['rally']['synId'])
    syn_test_helper_session.dispose_of(rally_project)

    rally = Rally.from_project(rally_project)

    rally_team = syn_client.getTeam(rally.rallyTeamId)
    syn_test_helper_session.dispose_of(rally_team)
