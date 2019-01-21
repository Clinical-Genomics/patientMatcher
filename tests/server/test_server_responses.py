# -*- coding: utf-8 -*-
import requests
import json
import pymongo
from werkzeug.datastructures import Headers
from patientMatcher import create_app
from patientMatcher.utils.add import add_node, load_demo
from patientMatcher.auth.auth import authorize
from patientMatcher.server.controllers import validate_response

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

    # send a malformed json object using a valid auth token
    malformed_json = "{'_id': 'patient_id' }"
    response = app.test_client().post('patient/add', data=malformed_json, headers = get_headers(demo_node['auth_token']))
    # and check that you get the correct error code from server(400)
    assert response.status_code == 400

    # add a patient not conforming to MME API using a valid auth token
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
    assert database['patients'].find({'label' : 'Patient number 1'}).count() == 1

    # modify patient label and check the update command (add a patient with the same id) works
    patient_data['label'] = 'modified patient label'
    patient_obj = {'patient' : patient_data}
    response = app.test_client().post('patient/add', data=json.dumps(patient_obj), headers = get_headers(demo_node['auth_token']))
    assert response.status_code == 200

    # There should still be one patient in database
    assert database['patients'].find().count() == 1

    # But its label is changed
    assert database['patients'].find({'label' : 'Patient number 1'}).count() == 0
    assert database['patients'].find({'label' : 'modified patient label'}).count() == 1


<<<<<<< HEAD
def test_delete_patient(database, demo_data_path, demo_node):
    """Test deleting a patient from database by sending a DELETE request"""

    app.db = database
    # load demo data to mock database using function located under utils/load
    inserted_ids = load_demo(demo_data_path, database)
    assert len(inserted_ids) == 50 # 50 test cases should be loaded

    # 50 cases present on patients collection
    assert database['patients'].find().count() == 50

    delete_id = inserted_ids[0]

    # try to delete patient without auth token:
    response = app.test_client().delete(''.join(['patient/delete/', delete_id]))
    assert response.status_code == 401

    # Add a valid client node
    ok_token = demo_node['auth_token']
    add_node(mongo_db=app.db, id=demo_node['_id'], token=ok_token,
        is_client=True, url=demo_node['base_url'], contact=demo_node['contact_email'])

    # Send delete request providing a valid token
    response = app.test_client().delete(''.join(['patient/delete/', delete_id]), headers = get_headers(ok_token))
=======
def test_delete_patient():
    # send a DELETE request to patient delete view
    response = app.test_client().delete('patient/delete')
>>>>>>> 4a5a3218afdf929ec56131481905260363564460
    assert response.status_code == 200

    # make sure that the patient was removed from database
    assert database['patients'].find().count() == 49


def test_patient_matches():
    # send a GET request to patient matches view
    response = app.test_client().get('patient/matches')
    assert response.status_code == 200
    # yet to be implemented!


def test_match_view(json_patients, demo_node, demo_data_path, database):
    """Testing patient matching against patientMatcher database (internal match)"""
    app.db = database

    # add an authorized client to database
    ok_token = demo_node['auth_token']
    add_node(mongo_db=app.db, id=demo_node['_id'], token=ok_token,
        is_client=True, url=demo_node['base_url'], contact=demo_node['contact_email'])

    query_patient = {'patient' : json_patients[0]}

    # load demo data in mock database
    inserted_ids = load_demo(demo_data_path, database, False)

    # test the API response validator with non valid patient data:
    malformed_match_results = 'fakey result'
    assert validate_response(malformed_match_results) == 422

    # send a POST request to match patient with patients in database
    response = app.test_client().post('/match', data=json.dumps(query_patient), headers = get_headers(demo_node['auth_token']))
    assert response.status_code == 200 # POST request should be successful
    data = json.loads(response.data)
    assert data['results'] # data should contain results object
    assert type(data['results']) == list # which is a list
    assert 'patient' in data['results'][0] # of patients
    assert 'score' in data['results'][0] # with matching scores


def test_external_match_view():
    # send a POST request to the internal match view
    response = app.test_client().post('/match/external')
    assert response.status_code == 200
    # yet to be implemented!


def get_headers(test_token):
    head = {'X-Auth-Token': test_token}
    return head
