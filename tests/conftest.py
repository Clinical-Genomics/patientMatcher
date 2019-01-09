# -*- coding: utf-8 -*-

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
def database(request, pymongo_client):
    """Get an adapter connected to mongo database"""
    mongo_client = pymongo_client
    database = mongo_client[DATABASE]
    return database


@pytest.fixture(scope='function')
def demo_data_path():
    root_dir = Path(__file__).resolve().parents[1]
    return os.path.join(root_dir, 'patientMatcher', 'resources', 'benchmark_patients.json')
