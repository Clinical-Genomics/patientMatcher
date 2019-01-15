# -*- coding: utf-8 -*-
import requests
import pymongo
from werkzeug.datastructures import Headers
from patientMatcher import create_app
from patientMatcher.utils.add import add_node
from patientMatcher.auth.auth import authorize

app = create_app()

def test_patient_view(database, demo_node):

    app.db = database
    # send a get request without being authorized
    response = app.test_client().get('patient/view')
    assert response.status_code == 401

    # add an authorized client to database
    ok_token = demo_node['auth_token']

    add_node(mongo_db=app.db, id=demo_node['_id'], token=ok_token,
        is_client=True, url=demo_node['base_url'], contact=demo_node['contact_email'])

    # make sure that database contains at least one client with auth_token == demo_node['auth_token']
    clients = app.db['clients'].find({'auth_token' : ok_token }).count()
    assert clients > 0

    # if a valid token is provided the server should return a status code 200 (success)
    auth_response = app.test_client().get('patient/view', headers = get_headers(demo_node['auth_token']))
    assert auth_response.status_code == 200


def test_add_patient():
    # send a POST request to patient add view
    response = app.test_client().post('patient/add')
    assert response.status_code == 200
    # yet to be implemented!


def test_delete_patient():
    # send a DELETE request to patient delete view
    response = app.test_client().delete('patient/delete')
    assert response.status_code == 200
    # yet to be implemented!


def test_patient_matches():
    # send a GET request to patient matches view
    response = app.test_client().get('patient/matches')
    assert response.status_code == 200
    # yet to be implemented!


def test_match_view():
    # send a POST request to the external match view
    response = app.test_client().post('/match')
    assert response.status_code == 200
    # yet to be implemented!


def test_internal_match_view():
    # send a POST request to the internal match view
    response = app.test_client().post('/match/internal')
    assert response.status_code == 200
    # yet to be implemented!
















def get_headers(test_token):
    head = {'X-Auth-Token': test_token}
    return head
