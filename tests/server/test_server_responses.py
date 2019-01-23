# -*- coding: utf-8 -*-
import requests
import json
import pymongo
from werkzeug.datastructures import Headers
from patientMatcher import create_app
from patientMatcher.utils.add import add_node, load_demo
from patientMatcher.auth.auth import authorize
from patientMatcher.server.controllers import validate_response
from patientMatcher.parse.patient import mme_patient

app = create_app()

def test_patient_view(database, test_client):
    """Testing viewing the list of patients on server for authorized users"""

    app.db = database
    # send a get request without being authorized
    response = app.test_client().get('patient/view')
    assert response.status_code == 401

    # add an authorized client to database
    ok_token = test_client['auth_token']

    add_node(mongo_db=app.db, obj=test_client, is_client=True)

    # make sure that database contains at least one client with auth_token == test_client['auth_token']
    clients = app.db['clients'].find({'auth_token' : ok_token }).count()
    assert clients > 0

    # if a valid token is provided the server should return a status code 200 (success)
    auth_response = app.test_client().get('patient/view', headers = get_headers(ok_token))
    assert auth_response.status_code == 200


def test_add_patient(database, json_patients, test_client, test_node):
    """Test sending a POST request to server to add a patient"""
    app.db = database

    patient_data = json_patients[0]
    # try to add a patient withou being authorized
    response = app.test_client().post('patient/add', data=json.dumps(patient_data))
    assert response.status_code == 401

    # add an authorized client to database
    ok_token = test_client['auth_token']

    add_node(mongo_db=app.db, obj=test_client, is_client=True)
    add_node(mongo_db=app.db, obj=test_node, is_client=False) # add a test node, to perform external matching

    # make sure there are no matchings in 'matches' collection
    assert database['matches'].find().count()==0

    # send a malformed json object using a valid auth token
    malformed_json = "{'_id': 'patient_id' }"
    response = app.test_client().post('patient/add', data=malformed_json, headers = get_headers(ok_token))
    # and check that you get the correct error code from server(400)
    assert response.status_code == 400

    # add a patient not conforming to MME API using a valid auth token
    response = app.test_client().post('patient/add', data=json.dumps(patient_data), headers = get_headers(ok_token))
    # and check that the server returns an error 422 (unprocessable entity)
    assert response.status_code == 422

    # check that patient collection in database is empty
    assert database['patients'].find().count() == 0

    patient_obj = {'patient' : patient_data} # this is a valid patient object
    response = app.test_client().post('patient/add', data=json.dumps(patient_obj), headers = get_headers(ok_token))
    assert response.status_code == 200

    # make sure that the POST request to add the patient triggers the matching request to an external node
    assert database['matches'].find().count()==1

    # There should be one patient in database now
    assert database['patients'].find().count() == 1
    # the patient in database has label "Patient number 2"
    assert database['patients'].find({'label' : 'Patient number 1'}).count() == 1

    # modify patient label and check the update command (add a patient with the same id) works
    patient_data['label'] = 'modified patient label'
    patient_obj = {'patient' : patient_data}
    response = app.test_client().post('patient/add', data=json.dumps(patient_obj), headers = get_headers(ok_token))
    assert response.status_code == 200

    # There should still be one patient in database
    assert database['patients'].find().count() == 1

    # But its label is changed
    assert database['patients'].find({'label' : 'Patient number 1'}).count() == 0
    assert database['patients'].find({'label' : 'modified patient label'}).count() == 1

    # make sure that the POST request to add modify patient triggers the matching request to an external node again
    assert database['matches'].find().count()==2


def test_delete_patient(database, demo_data_path, test_client):
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
    ok_token = test_client['auth_token']
    add_node(mongo_db=app.db, obj=test_client, is_client=True)

    # Send delete request providing a valid token but a non valid id
    response = app.test_client().delete(''.join(['patient/delete/', 'not_a_valid_ID']), headers = get_headers(ok_token))
    assert response.status_code == 200
    data = json.loads(response.data)
    # but server returns error
    assert data == 'ERROR. Could not delete a patient with ID not_a_valid_ID from database'

    # Send valid patient ID and valid token
    response = app.test_client().delete(''.join(['patient/delete/', delete_id]), headers = get_headers(ok_token))
    assert response.status_code == 200

    # make sure that the patient was removed from database
    assert database['patients'].find().count() == 49


def test_patient_matches():
    # send a GET request to patient matches view
    response = app.test_client().get('patient/matches')
    assert response.status_code == 200
    # yet to be implemented!


def test_match_view(json_patients, test_client, demo_data_path, database):
    """Testing patient matching against patientMatcher database (internal match)"""
    app.db = database

    # add an authorized client to database
    ok_token = test_client['auth_token']
    add_node(mongo_db=app.db, obj=test_client, is_client=True)

    query_patient = {'patient' : json_patients[0]}

    # load demo data in mock database
    inserted_ids = load_demo(demo_data_path, database, False)

    # test the API response validator with non valid patient data:
    malformed_match_results = 'fakey result'
    assert validate_response(malformed_match_results) == 422

    # make sure that there are no patient matches in the 'matches collection'
    assert database['matches'].find().count()==0

    # send a POST request to match patient with patients in database
    response = app.test_client().post('/match', data=json.dumps(query_patient), headers = get_headers(ok_token))
    assert response.status_code == 200 # POST request should be successful
    data = json.loads(response.data)
    assert data['results'] # data should contain results object
    assert type(data['results']) == list # which is a list
    assert 'patient' in data['results'][0] # of patients
    assert 'score' in data['results'][0] # with matching scores

    # make sure that there are match object is created in db for this internal matching
    assert database['matches'].find().count()==1


def test_match_external_view(test_client, test_node, database, json_patients):
    """Testing the view that is sending post request to trigger matches on external nodes"""
    app.db = database

    # add an authorized client to database
    ok_token = test_client['auth_token']
    add_node(mongo_db=app.db, obj=test_client, is_client=True) # required to trigger external matches
    add_node(mongo_db=app.db, obj=test_node, is_client=False) # required for external matches

    a_patient = json_patients[0]
    parsed_patient = mme_patient(a_patient)

    # insert patient into mock database:
    assert database['patients'].find().count() == 0
    inserted_id = database['patients'].insert_one(parsed_patient).inserted_id
    assert database['patients'].find().count() == 1

    # send an un-authorized match request to server
    response = app.test_client().post(''.join(['/match/external/', inserted_id]))
    # server should return 401 (not authorized)
    assert response.status_code == 401

    # send an authorized request with a patient ID that doesn't exist on server:
    response = app.test_client().post(''.join(['/match/external/', 'not_a_valid_ID']), headers = get_headers(ok_token))
    # Response is valid
    assert response.status_code == 200
    data = json.loads(response.data)
    # but server returns error
    assert data == 'ERROR. Could not find amy patient with ID not_a_valid_ID in database'

    # there are no matches in mock database
    assert database['matches'].find().count() == 0
    # after sending an authorized request with a patient ID that exists on database
    response = app.test_client().post(''.join(['/match/external/', inserted_id]), headers = get_headers(ok_token))
    # Response should be valid
    assert response.status_code == 200
    # And a new match should be created in matches collection
    assert database['matches'].find().count() == 1


def get_headers(test_token):
    head = {'X-Auth-Token': test_token}
    return head
