import pytest
import os
from src.core import Synapse
import synapseclient


def dispose_syn_project_from_body(body, synapse_test_helper):
    if body is None:
        return

    project_id = body.get('data', {}).get('createSynProject', {}).get('synProject', {}).get('id', None)
    if project_id:
        syn_project = Synapse.client().get(project_id)
        synapse_test_helper.dispose_of(syn_project)
        return syn_project
    else:
        return None


@pytest.fixture()
def gql_query():
    return '''
          mutation CreateSynProject($name: String!, $permissions: [PermissionDataInput], $annotations: [AnnotationDataInput], $wiki: WikiDataInput, $folders: [String], $posts: [PostDataInput]) {
            createSynProject(name: $name, permissions: $permissions, annotations: $annotations, wiki: $wiki, folders: $folders, posts: $posts) {
              synProject {
                id
                name
              }
              errors
            }
          }
        '''


@pytest.fixture()
def mk_gql_variables(synapse_test_helper):
    def _mk(with_all=False, with_permissions=False, with_annotations=False, with_wiki=False, with_folders=False,
            with_posts=False):
        name = synapse_test_helper.uniq_name(prefix='Syn Project ')
        vars = {
            'name': name,
            "permissions": None,
            "annotations": None,
            "wiki": None,
            "folders": None,
            "posts": None
        }

        if with_all or with_permissions:
            syn_team = synapse_test_helper.create_team()
            vars['permissions'] = [{"principalId": str(syn_team.id), "access": "ADMIN"}]

            other_test_user_id = os.environ.get('SYNAPSE_OTHER_USER_ID', None)
            if other_test_user_id:
                vars['permissions'].append({"principalId": int(other_test_user_id), "access": "CAN_EDIT"})
            else:
                print('WARNING: SYNAPSE_OTHER_USER_ID environment variable not set.')

        if with_all or with_annotations:
            vars['annotations'] = [{"key": "rally", "value": "1"}, {"key": "sprint", "value": "A"}]

        if with_all or with_wiki:
            vars['wiki'] = {'title': 'Main Wiki', 'markdown': 'main wiki markdown'}

        if with_all or with_folders:
            vars['folders'] = ['Folder1', 'Folder2', 'RootFolder/SubFolder1/SubFolder2']

        if with_all or with_posts:
            vars['posts'] = [{"title": "test1", "messageMarkdown": "markdown1"},
                             {"title": "test2", "messageMarkdown": "markdown2"}]
        return vars

    yield _mk


def test_it_creates_a_synapse_project(do_gql_post, gql_query, mk_gql_variables, synapse_test_helper, syn_client):
    # Just the project
    gql_variables = mk_gql_variables()

    body = do_gql_post(gql_query, gql_variables).get('body')
    assert body.get('errors', None) is None
    assert body['data']['createSynProject']['errors'] is None

    jsyn_project = body['data']['createSynProject']['synProject']
    assert jsyn_project['name'] == gql_variables.get('name')

    project = dispose_syn_project_from_body(body, synapse_test_helper)
    assert project.name == gql_variables.get('name')

    # The project and all properties
    gql_variables = mk_gql_variables(with_all=True)

    body = do_gql_post(gql_query, gql_variables).get('body')
    assert body.get('errors', None) is None
    assert body['data']['createSynProject']['errors'] is None
    assert dispose_syn_project_from_body(body, synapse_test_helper)


def test_it_creates_permissions(do_gql_post, gql_query, mk_gql_variables, synapse_test_helper, syn_client):
    gql_variables = mk_gql_variables(with_permissions=True)
    permissions = gql_variables.get('permissions')
    assert len(permissions) > 0

    body = do_gql_post(gql_query, gql_variables).get('body')
    assert body.get('errors', None) is None
    assert body['data']['createSynProject']['errors'] is None

    project = dispose_syn_project_from_body(body, synapse_test_helper)

    for permission in permissions:
        principal_id = permission['principalId']
        access = permission['access']
        access_type = getattr(Synapse, '{0}_PERMS'.format(access))

        perms = syn_client.getPermissions(project, principal_id)
        assert set(perms) == set(access_type)


def test_it_creates_annotations(do_gql_post, gql_query, mk_gql_variables, synapse_test_helper, syn_client):
    gql_variables = mk_gql_variables(with_annotations=True)
    annotations = gql_variables.get('annotations')
    assert len(annotations) > 0

    body = do_gql_post(gql_query, gql_variables).get('body')
    assert body.get('errors', None) is None
    assert body['data']['createSynProject']['errors'] is None

    project = dispose_syn_project_from_body(body, synapse_test_helper)

    for annotation in annotations:
        assert project.annotations[annotation['key']][0] == annotation['value']


def test_it_creates_the_wiki(do_gql_post, gql_query, mk_gql_variables, synapse_test_helper, syn_client):
    gql_variables = mk_gql_variables(with_wiki=True)
    wiki = gql_variables.get('wiki')
    assert wiki

    body = do_gql_post(gql_query, gql_variables).get('body')
    assert body.get('errors', None) is None
    assert body['data']['createSynProject']['errors'] is None

    project = dispose_syn_project_from_body(body, synapse_test_helper)

    main_wiki = syn_client.getWiki(project)
    assert main_wiki.title == wiki['title']
    assert main_wiki.markdown == wiki['markdown']


def test_it_creates_folders(do_gql_post, gql_query, mk_gql_variables, synapse_test_helper, syn_client):
    gql_variables = mk_gql_variables(with_folders=True)
    folders = gql_variables.get('folders')
    assert len(folders) > 0

    body = do_gql_post(gql_query, gql_variables).get('body')
    assert body.get('errors', None) is None
    assert body['data']['createSynProject']['errors'] is None

    project = dispose_syn_project_from_body(body, synapse_test_helper)

    for folder_path in folders:
        parent = project
        for folder_part in list(filter(None, folder_path.split('/'))):
            syn_folders = list(syn_client.getChildren(parent, includeTypes=['folder']))
            syn_folder = next((f for f in syn_folders if f.get('name') == folder_part), None)
            assert syn_folder
            assert syn_folder.get('name') == folder_part
            parent = syn_folder


def test_it_creates_posts(do_gql_post, gql_query, mk_gql_variables, synapse_test_helper, syn_client):
    gql_variables = mk_gql_variables(with_posts=True)
    posts = gql_variables.get('posts')
    assert len(posts) > 0

    body = do_gql_post(gql_query, gql_variables).get('body')
    assert body.get('errors', None) is None
    assert body['data']['createSynProject']['errors'] is None

    project = dispose_syn_project_from_body(body, synapse_test_helper)

    project_forum = syn_client.restGET('/project/{0}/forum'.format(project.id))
    threads = syn_client.restGET(
        '/forum/{0}/threads?limit=10&offset=0&filter=NO_FILTER'.format(project_forum.get('id')))
    for thread in threads['results']:
        assert thread['title'] in [p['title'] for p in posts]


def test_it_errors_if_the_project_name_is_taken(do_gql_post, gql_query, mk_gql_variables, synapse_test_helper,
                                                syn_client):
    gql_variables = mk_gql_variables()

    syn_project = synapse_test_helper.create_project()
    name = syn_project.name

    gql_variables['name'] = name

    body = do_gql_post(gql_query, gql_variables).get('body')
    assert body.get('errors', None) is not None
    assert 'Another Synapse project with the name: {0} already exists.'.format(name) in [e['message'] for e in
                                                                                         body.get('errors')]


def test_it_creates_the_project_and_reports_permission_errors(do_gql_post,
                                                              gql_query,
                                                              mk_gql_variables,
                                                              synapse_test_helper,
                                                              mocker):
    gql_variables = mk_gql_variables(with_permissions=True)
    permissions = gql_variables['permissions']
    assert len(permissions) > 0

    # User/Team does not exist error.
    with mocker.mock_module.patch.object(Synapse.client(), 'setPermissions') as mock:
        mock.side_effect = Exception('a foreign key constraint fails')
        gql_variables['name'] = synapse_test_helper.uniq_name(prefix='New Project Name ')

        body = do_gql_post(gql_query, gql_variables).get('body')
        assert dispose_syn_project_from_body(body, synapse_test_helper)
        assert body.get('errors', None) is None
        jerrors = body['data']['createSynProject']['errors']
        assert jerrors
        for permission in permissions:
            assert 'User or Team ID: ' \
                   '{0} does not exist.'.format(permission['principalId']) in jerrors

    # General unknown error.
    with mocker.mock_module.patch.object(Synapse.client(), 'setPermissions') as mock:
        mock.side_effect = Exception('some random error')
        gql_variables['name'] = synapse_test_helper.uniq_name(prefix='New Project Name ')

        body = do_gql_post(gql_query, gql_variables).get('body')
        assert dispose_syn_project_from_body(body, synapse_test_helper)
        assert body.get('errors', None) is None
        jerrors = body['data']['createSynProject']['errors']
        assert jerrors
        for permission in permissions:
            assert 'Error setting permission for User or Team ID: {0}'.format(permission['principalId']) in jerrors


def test_it_creates_the_project_and_reports_folder_errors(do_gql_post,
                                                          gql_query,
                                                          mk_gql_variables,
                                                          synapse_test_helper,
                                                          mocker):
    gql_variables = mk_gql_variables(with_folders=True)
    folders = gql_variables['folders']
    assert len(folders) > 0

    _real_store = Synapse.client().store

    def _store_proxy(obj, **kwargs):
        if isinstance(obj, synapseclient.Folder) or isinstance(obj, synapseclient.Wiki):
            raise Exception('some random error')
        return _real_store(obj, **kwargs)

    with mocker.mock_module.patch.object(Synapse.client(), 'store', new=_store_proxy):
        body = do_gql_post(gql_query, gql_variables).get('body')
        assert dispose_syn_project_from_body(body, synapse_test_helper)
        assert body.get('errors', None) is None
        jerrors = body['data']['createSynProject']['errors']
        assert jerrors

        for folder_path in folders:
            for folder_part in list(filter(None, folder_path.split('/'))):
                assert 'Error creating project folder: {0}.'.format(folder_part) in jerrors


def test_it_creates_the_project_and_reports_wiki_errors(do_gql_post,
                                                        gql_query,
                                                        mk_gql_variables,
                                                        synapse_test_helper,
                                                        mocker):
    gql_variables = mk_gql_variables(with_wiki=True)
    wiki = gql_variables['wiki']
    assert wiki

    _real_store = Synapse.client().store

    def _store_proxy(obj, **kwargs):
        if isinstance(obj, synapseclient.Folder) or isinstance(obj, synapseclient.Wiki):
            raise Exception('some random error')
        return _real_store(obj, **kwargs)

    with mocker.mock_module.patch.object(Synapse.client(), 'store', new=_store_proxy):
        body = do_gql_post(gql_query, gql_variables).get('body')
        assert dispose_syn_project_from_body(body, synapse_test_helper)
        assert body.get('errors', None) is None
        jerrors = body['data']['createSynProject']['errors']
        assert jerrors
        assert 'Error creating project wiki.' in jerrors


def test_it_creates_the_project_and_reports_posts_errors(do_gql_post,
                                                         gql_query,
                                                         mk_gql_variables,
                                                         synapse_test_helper,
                                                         mocker):
    gql_variables = mk_gql_variables(with_posts=True)
    posts = gql_variables['posts']
    assert len(posts) > 0

    _real_restGET = Synapse.client().restGET

    def _restGET_proxy(uri, endpoint=None, headers=None, retryPolicy={}, **kwargs):
        if '/forum' in uri:
            raise Exception('some random error')
        return _real_restGET(uri, endpoint=endpoint, headers=headers, retryPolicy=retryPolicy, **kwargs)

    with mocker.mock_module.patch.object(Synapse.client(), 'restGET', new=_restGET_proxy):
        gql_variables['name'] = synapse_test_helper.uniq_name(prefix='New Project Name ')
        body = do_gql_post(gql_query, gql_variables).get('body')
        assert dispose_syn_project_from_body(body, synapse_test_helper)
        assert body.get('errors', None) is None
        jerrors = body['data']['createSynProject']['errors']
        assert jerrors
        assert 'Error creating projects posts.' in jerrors

    _real_restPOST = Synapse.client().restPOST

    def _restPOST_proxy(uri, body, endpoint=None, headers=None, retryPolicy={}, **kwargs):
        if '/thread' in uri:
            raise Exception('some random error')
        return _real_restPOST(uri, body, endpoint=endpoint, headers=headers, retryPolicy=retryPolicy,
                              **kwargs)

    with mocker.mock_module.patch.object(Synapse.client(), 'restPOST', new=_restPOST_proxy):
        gql_variables['name'] = synapse_test_helper.uniq_name(prefix='New Project Name ')
        body = do_gql_post(gql_query, gql_variables).get('body')
        assert dispose_syn_project_from_body(body, synapse_test_helper)
        assert body.get('errors', None) is None
        jerrors = body['data']['createSynProject']['errors']
        assert jerrors
        for post in posts:
            assert 'Error creating project post: {0}.'.format(post.get('title')) in jerrors
