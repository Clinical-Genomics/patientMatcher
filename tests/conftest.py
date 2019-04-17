# -*- coding: utf-8 -*-
import os
import pytest
import mongomock
from pathlib import Path
from patientMatcher.server import create_app
from patientMatcher.resources import path_to_benchmark_patients

DATABASE = 'testdb'

class MockMail:
    _send_was_called = False
    _message = None

    def send(self, message):
        self._send_was_called = True
        self._message = message

@pytest.fixture
def mock_app(database, pymongo_client):
    app = create_app()
    app.db = database
    app.client = pymongo_client
    return app

@pytest.fixture
def mock_mail():
    return MockMail()

@pytest.fixture
def mock_sender():
    return 'mock_sender'

@pytest.fixture(scope='function')
def pymongo_client(request):
    """Get a client to the mongo database"""
    mock_client = mongomock.MongoClient()
    def teardown():
        mock_client.drop_database(DATABASE)
    request.addfinalizer(teardown)
    return mock_client

@pytest.fixture(scope='function')
def database(request, pymongo_client):
    """Get an adapter connected to mongo database"""
    mongo_client = pymongo_client
    database = mongo_client[DATABASE]
    return database


@pytest.fixture(scope='function')
def demo_data_path():
    return path_to_benchmark_patients


@pytest.fixture(scope='function')
def test_client():
    """Returns a test client object"""
    client = {
        '_id' : 'client_1',
        'auth_token' : 'superSecretToken',
        'base_url' : 'http://test_node_institution.com',
        'contact' : 'test_client@email.com'
    }
    return client


@pytest.fixture(scope='function')
def test_node():
    """Returns a test client object"""
    node = {
        '_id' : 'node_1',
        'label' : 'Test node description',
        'auth_token' : 'superSecretToken',
        'matching_url' : 'http://test_node/match/',
        'accepted_content' : 'application/vnd.ga4gh.matchmaker.v1.0+json',
        'contact' : 'test_node_user@email.com'
    }
    return node


@pytest.fixture(scope='function')
def match_objs():
    """Mock the results of an internal and an external match"""
    matches = [
        {    # External match where test_patient is the query and with results
            '_id' : 'match_1',
            'has_matches' : True,
            'data' : {
                'patient' : {
                    'id' : 'P0000079',
                    'contact' : {
                        'href' : 'mailto:test_contact@email.com'
                    }
                }
            },
            'results' : [
                {
                    'node' : {'id' : 'test_node1', 'label': 'Test Node 1'},
                    'patients' : [
                        {'patient' : { 'patient_data1' : 'test_stuff1'}},
                        {'patient' : { 'patient_data2' : 'test_stuff2'}}
                    ]
                },
                {
                    'node' : {'id' : 'test_node2', 'label': 'Test Node 2'},
                    'patients' : [
                        {'patient' : { 'patient_data3' : 'test_stuff3'}}
                    ]
                }
            ],
            'match_type' : 'external'
        },
        {    # Internal match where test_patient is the query and there are no results
            '_id' : 'match_2',
            'has_matches' : False,
            'data' : {
                'patient' : {
                    'id' : 'P0000079'
                },
                'contact' : {
                    'href' : 'mailto:test_contact@email.com'
                }
            },
            'results' : [
                {
                    'node': {'id' : 'patientMatcher', 'label' : 'patientMatcher server'},
                    'patients' : [
                        {'patient' : { 'int_pat1' : 'test_stuff'}}
                    ]
                }
            ],
            'match_type' : 'internal'
        },
        {    #  Internal match where test_patient is among results
            '_id' : 'match_3',
            'has_matches' : True,
            'data' : {
                'patient' : {
                    'id' : 'external_patient_1',
                    'contact' : {
                        'href' : 'mailto:test_contact@email.com'
                    }
                }
            },
            'results' : [
                {
                    'node' : {'id' : 'test_node1', 'label': 'Test Node 1'},
                    'patients' : [
                        {'patient' : {
                            'id' : 'P0000079',
                            'contact' : {
                                'href' : 'mailto:test_contact2@email.com'
                            }
                        }}
                    ]
                }
            ],
            'match_type' : 'internal'
        },
    ]
    return matches


@pytest.fixture(scope='function')
def json_patients():
    """ returns a list containing two matchmaker-like patient objects """
    fakey_patients = [
    {
        "contact": {
          "href": "mailto:contact_email@email.com",
          "name": "A contact at an institute"
        },
        "features": [
          {
            "id": "HP:0010943",
            "label": "Echogenic fetal bowel",
            "observed": "yes"
          }
        ],
        "disorders": [
            {
                "id" : "MIM:616007"
            }
        ],
        "genomicFeatures": [
        {
            "gene": {
              "id": "LIMS2"
            },
            "type": {
              "id": "SO:0001583",
              "label": "MISSENSE"
            },
            "variant": {
              "alternateBases": "C",
              "assembly": "GRCh37",
              "end": 128412081,
              "referenceBases": "G",
              "referenceName": "2",
              "start": 128412080
            },
            "zygosity": 1
        },
        {
            "gene": {
              "id": "LIMS2"
            },
            "type": {
              "id": "SO:0001583",
              "label": "MISSENSE"
            },
            "variant": {
              "alternateBases": "A",
              "assembly": "GRCh37",
              "end": 128412067,
              "referenceBases": "G",
              "referenceName": "2",
              "start": 128412066
            },
            "zygosity": 1
        },
        {
            "gene": {
              "id": "KARS"
            },
            "type": {
              "id": "SO:0001583",
              "label": "MISSENSE"
            },
            "variant": {
              "alternateBases": "A",
              "assembly": "GRCh37",
              "end": 75665092,
              "referenceBases": "G",
              "referenceName": "16",
              "start": 75665091
            },
            "zygosity": 1
        }],
        "id": "patient_1",
        "label": "Patient number 1"
    },
    {
        "contact": {
          "href": "mailto:contact_email@email.com",
          "name": "A contact at an institute"
        },
        "features": [
          {
            "id": "HP:0001644",
            "label": "Dilated cardiomyopathy",
            "observed": "yes"
          },
        ],
        "genomicFeatures": [
          {
            "gene": {
              "id": ""
            },
            "type": {
              "id": "SO:0001583",
              "label": "MISSENSE"
            },
            "variant": {
              "alternateBases": "C",
              "assembly": "GRCh37",
              "end": 128412081,
              "referenceBases": "G",
              "referenceName": "2",
              "start": 128412080
            },
            "zygosity": 1
          },
        ],
        "id": "patient_2",
        "label": "Patient number 2"
    }]
    return fakey_patients


@pytest.fixture(scope='function')
def async_response_obj(test_node, json_patients):
    """Returns the object written to database when sending a match request to
    an async server"""

    async_response = {
        '_id' : 'async_obj_id',
        'query_id' : 'test_query_id',
        'node' : {
            'id' : test_node['_id'],
            'label' : test_node['label']
        },
        'query_patient_id' : json_patients[0]['id'],
    }
    return async_response
