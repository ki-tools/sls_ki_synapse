import pytest
from handlers import handler
from synapseclient import EntityViewSchema, Schema, Column, Table, Row, RowSet
import time
from data.rally.types import Rally


def test_query_rally(rally_project, rally_setup):
    rally = Rally.from_project(rally_project)

    q = '''
        query {
            rally(rallyAdminProjectId: "%s", rallyNumber: %s) {
                synId
                number
                title
            }
        }
    ''' % (rally_setup['rally_admin_project'].id, rally.number)

    resp = handler.graphql(q, None)
    assert not resp.errors
    assert resp.data['rally'] != None
    assert resp.data['rally']['synId'] == rally_project.id


def test_create_rally(rally_setup, rally_number, syn_client, syn_test_helper_session):
    rallyNumber = rally_number
    consortium = rally_setup['rally_config']['consortium']
    rallyAdminProjectId = rally_setup['rally_admin_project'].id
    wikiTaskTemplateId = rally_setup['master_task_wiki_template'].id
    wikiRallyTemplateId = rally_setup['master_rally_wiki_template'].id
    allFilesSchemaId = rally_setup['all_files_schema'].id
    defaultRallyTeamMembers = rally_setup['rally_config']['defaultRallyTeamMembersStr']
    rallyAdminTeamPermissions = rally_setup['rally_config']['rallyAdminTeamPermissionsStr']
    sprintFolders = rally_setup['rally_config']['sprintFoldersStr']
    posts = rally_setup['rally_config']['postsStr']

    q = '''
       mutation createNewRally {
        createRally(rallyNumber: %s, consortium: "%s", rallyAdminProjectId: "%s", wikiTaskTemplateId: "%s", wikiRallyTemplateId: "%s", allFilesSchemaId: "%s", defaultRallyTeamMembers: [%s], rallyAdminTeamPermissions: [%s], sprintFolders: [%s], posts: [%s]) {
            rally {
                synId
                number
                title
            }
            ok
        }
    }
    ''' % (rallyNumber, consortium, rallyAdminProjectId, wikiTaskTemplateId, wikiRallyTemplateId, allFilesSchemaId, defaultRallyTeamMembers, rallyAdminTeamPermissions, sprintFolders, posts)

    resp = handler.graphql(q, None)
    assert not resp.errors

    # Get the project and team so they can be deleted.
    rally_project = syn_client.get(resp.data['createRally']['rally']['synId'])
    syn_test_helper_session.dispose_of(rally_project)

    rally = Rally.from_project(rally_project)

    rally_team = syn_client.getTeam(rally.rallyTeamId)
    syn_test_helper_session.dispose_of(rally_team)
