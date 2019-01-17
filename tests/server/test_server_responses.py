# -*- coding: utf-8 -*-
import requests
import json
import pymongo
from werkzeug.datastructures import Headers
from patientMatcher import create_app
from patientMatcher.utils.add import add_node
from patientMatcher.auth.auth import authorize

app = create_app()

def test_patient_view(database, demo_node):
    """Testing viewing the list of patients on server for authorized users"""

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


def test_add_patient(database, json_patients, demo_node):
    """Test sending a POST request to server to add a patient"""
    app.db = database

    patient_data = json_patients[0]
    # try to add a patient withou being authorized
    response = app.test_client().post('patient/add', data=json.dumps(patient_data))
    assert response.status_code == 401

    # add an authorized client to database
    ok_token = demo_node['auth_token']

    add_node(mongo_db=app.db, id=demo_node['_id'], token=ok_token,
        is_client=True, url=demo_node['base_url'], contact=demo_node['contact_email'])

    # add a malformed patient using a valid auth token
    response = app.test_client().post('patient/add', data=json.dumps(patient_data), headers = get_headers(demo_node['auth_token']))
    # and check that the server returns an error 422 (unprocessable entity)
    assert response.status_code == 422

    # check that patient collection in database is empty
    assert database['patients'].find().count() == 0

    patient_obj = {'patient' : patient_data} # this is a valid patient object
    response = app.test_client().post('patient/add', data=json.dumps(patient_obj), headers = get_headers(demo_node['auth_token']))
    assert response.status_code == 200

    # There should be one patient in database now
    assert database['patients'].find().count() == 1
    # the patient in database has label "Patient number 2"
    assert database['patients'].find({'label' : 'Patient number 2'}).count() == 1

    # modify patient label and check the update command (add a patient with the same id) works
    patient_data['label'] = 'modified patient label'
    patient_obj = {'patient' : patient_data}
    response = app.test_client().post('patient/add', data=json.dumps(patient_obj), headers = get_headers(demo_node['auth_token']))
    assert response.status_code == 200

    # There should still be one patient in database
    assert database['patients'].find().count() == 1

    # But its label is changed
    assert database['patients'].find({'label' : 'Patient number 2'}).count() == 0
    assert database['patients'].find({'label' : 'modified patient label'}).count() == 1









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
