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
import responses
from moto import mock_s3
from core import ParamStore


@pytest.fixture()
def gql_query():
    return '''
          mutation CreateSlideDeck($title: String!, $presenter: String!, $sprintId: String!, $participants: [String]!, $endDate: String!, $sprintQuestions: [String]!, $background: String!, $problemStatement: String!, $motivation: String!, $deliverables: [String]!, $keyFindings: [String]!, $nextSteps: [String]!, $value: String!, $templateUrl: String) {
            createSlideDeck(title: $title, presenter: $presenter, sprintId: $sprintId, participants: $participants, endDate: $endDate, sprintQuestions: $sprintQuestions, background: $background, problemStatement: $problemStatement, motivation: $motivation, deliverables: $deliverables, keyFindings: $keyFindings, nextSteps: $nextSteps, value: $value, templateUrl: $templateUrl) {
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

        return vars

    yield _mk


@mock_s3
def test_it_creates_a_slide_deck_from_the_internal_template(do_gql_post, gql_query, mk_gql_variables, s3_client):
    # Create a mock bucket to store the ppt file.
    s3_client.create_bucket(Bucket=ParamStore.SLIDE_DECKS_BUCKET_NAME())

    gql_variables = mk_gql_variables()

    body = do_gql_post(gql_query, gql_variables).get('body')
    assert body.get('errors', None) is None
    jslide_deck = body['data']['createSlideDeck']['slideDeck']
    assert jslide_deck['url'] is not None
    assert ParamStore.SLIDE_DECKS_BUCKET_NAME() in jslide_deck['url']


@mock_s3
def test_it_creates_a_slide_deck_from_an_external_template(do_gql_post, gql_query, mk_gql_variables, s3_client):
    # Create a mock bucket to store the ppt file.
    s3_client.create_bucket(Bucket=ParamStore.SLIDE_DECKS_BUCKET_NAME())

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
        assert ParamStore.SLIDE_DECKS_BUCKET_NAME() in jslide_deck['url']
