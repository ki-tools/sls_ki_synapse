import pytest
from handlers import graphql_handler
from synapseclient import EntityViewSchema, Schema, Column, Table, Row, RowSet
import time
import json as JSON
from data.rally.types import (Rally, RallySprint)
from data.rally.queries import RallyQuery


def do_post(query, variables):
    """
    Executes a query against the handler.
    """
    event = {'query': query, 'variables': variables}
    context = None
    return JSON.loads(graphql_handler.graphql(event, context))


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

    resp = do_post(q, v)
    assert not resp.get('errors', None)
    assert resp['data']['rally']['synId'] == expected_syn_id


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

    resp = do_post(q, v)
    assert not resp.get('errors', None)
    assert resp['data']['rallySprint']['synId'] == expected_syn_id


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

    resp = do_post(q, v)
    assert not resp.get('errors', None)
    assert resp['data']['rally'] != None
    assert resp['data']['rally']['synId'] == rally.synId
    assert resp['data']['rally']['number'] == rally.number


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

    resp = do_post(q, v)
    assert not resp.get('errors', None)
    assert resp['data']['rallySprint'] != None
    assert resp['data']['rallySprint']['synId'] == rally_sprint.synId
    assert resp['data']['rallySprint']['letter'] == rally_sprint.letter


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

    # Remove the 'forumId' from the posts.
    # This value gets added when another tests uses a fixture that creates a sprint
    # TODO: Find a better way to handle this.
    for post in posts:
        post.pop('forumId', None)

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

    resp = do_post(q, v)
    assert not resp.get('errors', None)

    # Get the project and team so they can be deleted.
    rally_project = syn_client.get(
        resp['data']['createRally']['rally']['synId'])
    syn_test_helper_session.dispose_of(rally_project)

    rally = Rally.from_project(rally_project)

    rally_team = syn_client.getTeam(rally.rallyTeamId)
    syn_test_helper_session.dispose_of(rally_team)


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
      mutation CreateNewRallySprint($rallyNumber: Int!, $sprintLetter: String!, $consortium: String!, $rallyAdminProjectId: String!, $wikiTaskTemplateId: String!, $wikiRallyTemplateId: String!, $allFilesSchemaId: String!, $defaultRallyTeamMembers: [Int]!, $rallyAdminTeamPermissions: [String]!, $sprintFolders: [String]!, $posts: [PostDataInput]!) {
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

    resp = do_post(q, v)
    assert not resp.get('errors', None)

    # Get the project and team so they can be deleted.
    rally_project_sprint = syn_client.get(
        resp['data']['createRallySprint']['rallySprint']['synId'])
    syn_test_helper_session.dispose_of(rally_project_sprint)
