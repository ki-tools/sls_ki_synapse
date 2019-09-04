import pytest
import os
from core import Synapse


@pytest.fixture()
def gql_query():
    return '''
      mutation UpdateSynProject($id: String!, $name: String, $permissions: [PermissionDataInput]) {
        updateSynProject(id: $id, name: $name, permissions: $permissions) {
          synProject {
            id
            name
          }
          errors
        }
      }
    '''


@pytest.fixture()
def mk_gql_variables(syn_test_helper):
    def _mk(syn_project, name=None, with_permissions=False):
        name = name or syn_test_helper.uniq_name(prefix='Syn Project ')

        vars = {
            "id": syn_project.id,
            "name": name,
            "permissions": None
        }

        if with_permissions:
            syn_team = syn_test_helper.create_team()
            vars['permissions'] = [{"principalId": str(syn_team.id), "access": "ADMIN"}]

            other_test_user_id = os.environ.get('SYNAPSE_OTHER_USER_ID', None)
            if other_test_user_id:
                vars['permissions'].append({"principalId": int(other_test_user_id), "access": "CAN_EDIT"})
            else:
                print('WARNING: SYNAPSE_OTHER_USER_ID environment variable not set.')

        return vars

    yield _mk


def test_it_updates_the_project_name(do_gql_post, gql_query, mk_gql_variables, syn_test_helper, syn_client):
    project = syn_test_helper.create_project()

    gql_variables = mk_gql_variables(project)
    new_name = gql_variables.get('name')
    assert project.name != new_name

    body = do_gql_post(gql_query, gql_variables).get('body')
    assert body.get('errors', None) is None
    jsyn_project = body['data']['updateSynProject']['synProject']
    assert jsyn_project['name'] == new_name

    # Reload the project
    project = syn_client.get(project)
    assert project.name == new_name


def test_it_adds_and_removes_permissions(do_gql_post, gql_query, mk_gql_variables, syn_test_helper, syn_client):
    project = syn_test_helper.create_project()

    gql_variables = mk_gql_variables(project, with_permissions=True)
    permissions = gql_variables.get('permissions')
    assert len(permissions) > 0

    body = do_gql_post(gql_query, gql_variables).get('body')
    assert body.get('errors', None) is None

    for permission in permissions:
        principal_id = permission['principalId']
        access = permission['access']
        access_type = getattr(Synapse, '{0}_PERMS'.format(access))

        perms = syn_client.getPermissions(project, principal_id)
        assert set(perms) == set(access_type)

    # Make sure permissions are removed
    removed_perm = permissions.pop()

    body = do_gql_post(gql_query, gql_variables).get('body')
    assert body.get('errors', None) is None

    acl = Synapse.client()._getACL(project)

    current_principal_ids = [int(r['principalId']) for r in acl['resourceAccess']]

    assert int(removed_perm['principalId']) not in current_principal_ids


def test_it_updates_the_project_and_reports_permission_errors(do_gql_post,
                                                              gql_query,
                                                              mk_gql_variables,
                                                              syn_test_helper,
                                                              mocker):
    project = syn_test_helper.create_project()

    gql_variables = mk_gql_variables(project, with_permissions=True)
    permissions = gql_variables['permissions']
    assert len(permissions) > 0

    # User/Team does not exist error.
    with mocker.mock_module.patch.object(Synapse.client(), 'setPermissions') as mock:
        mock.side_effect = Exception('a foreign key constraint fails')
        gql_variables['name'] = syn_test_helper.uniq_name(prefix='New Project Name ')

        body = do_gql_post(gql_query, gql_variables).get('body')
        assert body.get('errors', None) is None
        jerrors = body['data']['updateSynProject']['errors']
        assert jerrors
        for permission in permissions:
            assert 'User or Team ID: ' \
                   '{0} does not exist.'.format(permission['principalId']) in jerrors

    # General unknown error.
    with mocker.mock_module.patch.object(Synapse.client(), 'setPermissions') as mock:
        mock.side_effect = Exception('some random error')
        gql_variables['name'] = syn_test_helper.uniq_name(prefix='New Project Name ')

        body = do_gql_post(gql_query, gql_variables).get('body')
        assert body.get('errors', None) is None
        jerrors = body['data']['updateSynProject']['errors']
        assert jerrors
        for permission in permissions:
            assert 'Error setting permission for User or Team ID: {0}'.format(permission['principalId']) in jerrors
