# -*- coding: utf-8 -*-

from patientMatcher.utils.add import add_node

def test_add_client(database, demo_node):
    """Test adding a client with auth token to the database"""

    is_client = True
    test_node = demo_node

    # no clients should be present in demo database
    nclients = database['clients'].find().count()
    assert nclients == 0

    inserted_id, collection = add_node(mongo_db=database, id=test_node['_id'], token=test_node['auth_token'],
        is_client=is_client, url=test_node['base_url'], contact=test_node['contact_email'])

    assert inserted_id == test_node['_id']
    assert collection == 'clients'
    nclients = database['clients'].find().count()
    assert nclients == 1

    # make sure that once a node is inserted it's not possible to add another node with the same id
    inserted_id, collection = add_node(mongo_db=database, id=test_node['_id'], token=test_node['auth_token'],
        is_client=is_client, url=test_node['base_url'], contact=test_node['contact_email'])
    assert inserted_id == None


def test_add_server(database, demo_node):
    """Test adding a server with auth token to the database"""

    is_client = False
    test_node = demo_node

    # no server should be present in demo database
    nservers = database['nodes'].find().count()
    assert nservers == 0

    inserted_id, collection = add_node(mongo_db=database, id=test_node['_id'], token=test_node['auth_token'],
        is_client=is_client, url=test_node['base_url'], contact=test_node['contact_email'])

    assert inserted_id == test_node['_id']
    assert collection == 'nodes'
    nservers = database['nodes'].find().count()
    assert nservers == 1

    # make sure that once a node is inserted it's not possible to add another node with the same id
    inserted_id, collection = add_node(mongo_db=database, id=test_node['_id'], token=test_node['auth_token'],
        is_client=is_client, url=test_node['base_url'], contact=test_node['contact_email'])
    assert inserted_id == None
