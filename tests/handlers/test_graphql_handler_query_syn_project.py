import pytest
from data.syn_project import SynProject, SynProjectQuery


@pytest.fixture()
def gql_query():
    return """
        query GetSynProject($id: String!) {
            synProject(id: $id) {
                id
                name
            }
        }
    """


@pytest.fixture()
def mk_gql_variables():
    def _mk(id):
        vars = {
            'id': id
        }

        return vars

    yield _mk


def test_handler_get_syn_project(do_gql_post, gql_query, mk_gql_variables, mocker):
    gql_variables = mk_gql_variables('1')

    expected_syn_id = 'syn000'
    expected_name = 'A Test Name'

    mock = mocker.patch.object(SynProjectQuery, 'resolve_syn_project')
    mock.return_value = SynProject(id=expected_syn_id, name=expected_name)

    body = do_gql_post(gql_query, gql_variables).get('body')
    assert body.get('errors', None) is None
    assert body['data']['synProject']['id'] == expected_syn_id
    assert body['data']['synProject']['name'] == expected_name


def test_returns_a_syn_project(do_gql_post, gql_query, mk_gql_variables, syn_test_helper):
    project = syn_test_helper.create_project()
    gql_variables = mk_gql_variables(project.id)

    body = do_gql_post(gql_query, gql_variables).get('body')
    assert body.get('errors', None) is None
    assert body['data']['synProject'] is not None
    assert body['data']['synProject']['id'] == project.id
    assert body['data']['synProject']['name'] == project.name
