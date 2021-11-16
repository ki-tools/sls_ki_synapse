import pytest
import responses
from moto import mock_s3
from core import Env


@pytest.fixture()
def gql_query():
    return '''
          mutation CreateSlideDeck($title: String!, $sprintId: String!, $participants: [String]!, $endDate: String!, $sprintQuestions: [String]!, $background: String!, $deliverables: [String]!, $keyFindings: [String]!, $nextSteps: [String]!, $value: String!, $templateUrl: String) {
            createSlideDeck(title: $title, sprintId: $sprintId, participants: $participants, endDate: $endDate, sprintQuestions: $sprintQuestions, background: $background, deliverables: $deliverables, keyFindings: $keyFindings, nextSteps: $nextSteps, value: $value, templateUrl: $templateUrl) {
                slideDeck {
                    url
                }
            }
        }
        '''


@pytest.fixture()
def mk_gql_variables(syn_test_helper):
    def _mk():
        vars = {
            'title': 'My Title',
            'sprintId': 'A',
            'participants': ['Name1', 'Name2', 'Name3'],
            'endDate': '2018-01-01',
            'sprintQuestions': ['Question1', 'Question2', 'Question3'],
            'background': 'Some Background Info',
            'deliverables': ['Deliverable1', 'Deliverable2', 'Deliverable3'],
            'keyFindings': ['Finding1', 'Finding2', 'Finding3'],
            'nextSteps': ['Step1', 'Step2', 'Step3'],
            'value': 'Some Value'
        }

        return vars

    yield _mk


@mock_s3
def test_it_creates_a_slide_deck_from_the_internal_template(do_gql_post, gql_query, mk_gql_variables, s3_client):
    # Create a mock bucket to store the ppt file.
    s3_client.create_bucket(Bucket=Env.SLIDE_DECKS_BUCKET_NAME(),
                            CreateBucketConfiguration={'LocationConstraint': 'us-west-1'})

    gql_variables = mk_gql_variables()

    body = do_gql_post(gql_query, gql_variables).get('body')
    assert body.get('errors', None) is None
    jslide_deck = body['data']['createSlideDeck']['slideDeck']
    assert jslide_deck['url'] is not None
    assert Env.SLIDE_DECKS_BUCKET_NAME() in jslide_deck['url']


@mock_s3
def test_it_creates_a_slide_deck_from_an_external_template(do_gql_post, gql_query, mk_gql_variables, s3_client):
    # Create a mock bucket to store the ppt file.
    s3_client.create_bucket(Bucket=Env.SLIDE_DECKS_BUCKET_NAME(),
                            CreateBucketConfiguration={'LocationConstraint': 'us-west-1'})

    template_url = 'https://afakedomainname.com/file.pptx'
    gql_variables = mk_gql_variables()
    gql_variables['templateUrl'] = template_url

    with open('assets/template_ki_empty.pptx', 'rb') as f:
        pptx = f.read()

    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, template_url, body=pptx, status=200)

        body = do_gql_post(gql_query, gql_variables).get('body')
        assert body.get('errors', None) is None
        jslide_deck = body['data']['createSlideDeck']['slideDeck']
        assert jslide_deck['url'] is not None
        assert Env.SLIDE_DECKS_BUCKET_NAME() in jslide_deck['url']
