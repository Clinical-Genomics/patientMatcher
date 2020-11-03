# -*- coding: utf-8 -*-

from patientMatcher.utils.add import add_node


def test_add_client(database, test_client):
    """Test adding a client with auth token to the database"""

    is_client = True

    # no clients should be present in demo database
    assert database["clients"].find_one() is None

    inserted_id, collection = add_node(mongo_db=database, obj=test_client, is_client=is_client)

    assert inserted_id == test_client["_id"]
    assert collection == "clients"
    assert database["clients"].find_one()

    # make sure that once a node is inserted it's not possible to add another node with the same id
    inserted_id, collection = add_node(mongo_db=database, obj=test_client, is_client=True)
    assert inserted_id == None


def test_add_server(database, test_node):
    """Test adding a server with auth token to the database"""

    is_client = False

    # no server should be present in demo database
    assert database["nodes"].find_one() is None

    inserted_id, collection = add_node(mongo_db=database, obj=test_node, is_client=is_client)

    assert inserted_id == test_node["_id"]
    assert collection == "nodes"
    assert database["nodes"].find_one()

    # make sure that once a node is inserted it's not possible to add another node with the same id
    inserted_id, collection = add_node(mongo_db=database, obj=test_node, is_client=is_client)
    assert inserted_id == None
