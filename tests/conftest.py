# -*- coding: utf-8 -*-

from click.testing import CliRunner
import os
import pytest
import mongomock
from pathlib import Path

DATABASE = 'testdb'

@pytest.fixture(scope='function')
def pymongo_client(request):
    """Get a client to the mongo database"""
    mock_client = mongomock.MongoClient()
    def teardown():
        mock_client.drop_database(DATABASE)
    request.addfinalizer(teardown)
    return mock_client


@pytest.fixture(scope='function')
def runner():
    return CliRunner()


@pytest.fixture(scope='function')
def database(request, pymongo_client):
    """Get an adapter connected to mongo database"""
    mongo_client = pymongo_client
    database = mongo_client[DATABASE]
    return database


@pytest.fixture(scope='function')
def demo_data_path():
    root_dir = Path(__file__).resolve().parents[1]
    return os.path.join(root_dir, 'patientMatcher', 'resources', 'benchmark_patients.json')


@pytest.fixture(scope='function')
def demo_node():
    """Returns a server or a client object"""
    node = {
        '_id' : 'test_node',
        'auth_token' : 'superSecretToken',
        'base_url' : 'test_node_institution.com',
        'contact_email' : 'test_node@email.com'
    }
    return node


@pytest.fixture(scope='function')
def json_patients():
    """ returns a list containing two matchmaker-like patient objects """
    fakey_patients = [
    {
        "contact": {
          "href": "mme_user@mail.com",
          "name": "Another user"
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
        "id": "patient_2",
        "label": "Patient number 2"
    },
    {
        "contact": {
          "href": "mme_user@mail.com",
          "name": "A User"
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
        "id": "patient_1",
        "label": "Patient number 1"
    }]
    return fakey_patients
