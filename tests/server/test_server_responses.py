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
from patientMatcher.match.handler import patient_matches

app = create_app()

def test_add_patient(database, json_patients, test_client, test_node):
    #Test sending a POST request to server to add a patient
    app.db = database

    patient_data = json_patients[0]
    # try to add a patient without being authorized
    response = app.test_client().post('patient/add', data=json.dumps(patient_data), headers=unauth_headers())
    assert response.status_code == 401

    # add an authorized client to database
    ok_token = test_client['auth_token']

    add_node(mongo_db=app.db, obj=test_client, is_client=True)
    add_node(mongo_db=app.db, obj=test_node, is_client=False) # add a test node, to perform external matching

    # make sure there are no matchings in 'matches' collection
    assert database['matches'].find().count()==0

    # send a malformed json object using a valid auth token
    malformed_json = "{'_id': 'patient_id' }"
    response = app.test_client().post('patient/add', data=malformed_json, headers = auth_headers(ok_token))
    # and check that you get the correct error code from server(400)
    assert response.status_code == 400

    # add a patient not conforming to MME API using a valid auth token
    response = app.test_client().post('patient/add', data=json.dumps(patient_data), headers = auth_headers(ok_token))
    # and check that the server returns an error 422 (unprocessable entity)
    assert response.status_code == 422

    # check that patient collection in database is empty
    assert database['patients'].find().count() == 0

    patient_obj = {'patient' : patient_data} # this is a valid patient object
    response = app.test_client().post('patient/add', data=json.dumps(patient_obj), headers = auth_headers(ok_token))
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
    response = app.test_client().post('patient/add', data=json.dumps(patient_obj), headers = auth_headers(ok_token))
    assert response.status_code == 200

    # There should still be one patient in database
    assert database['patients'].find().count() == 1

    # But its label is changed
    assert database['patients'].find({'label' : 'Patient number 1'}).count() == 0
    assert database['patients'].find({'label' : 'modified patient label'}).count() == 1

    # make sure that the POST request to add modify patient triggers the matching request to an external node again
    assert database['matches'].find().count()==2


def test_metrics(database, test_client, demo_data_path, match_objs):
    """Testing viewing the list of patients on server for authorized users"""

    app.db = database
    # send a get request without being authorized
    response = app.test_client().get('metrics')
    assert response.status_code == 401

    # add an authorized client to database
    ok_token = test_client['auth_token']

    add_node(mongo_db=app.db, obj=test_client, is_client=True)

    # make sure that database contains at least one client with auth_token == test_client['auth_token']
    clients = app.db['clients'].find({'auth_token' : ok_token }).count()
    assert clients > 0

    # load demo data of 50 test patients
    inserted_ids = load_demo(demo_data_path, database, app.config.get('MME_HOST'))
    assert len(inserted_ids) == 50 # 50 test cases should be loaded

    # load mock matches into database
    database.matches.insert_many(match_objs)
    assert database.matches.find().count() == 3

    # if a valid token is provided the server should return metrics with patient data and matching results
    auth_response = app.test_client().get('metrics', headers = auth_headers(ok_token))
    assert auth_response.status_code == 200

    data = json.loads(auth_response.data)
    assert data['disclaimer'] # disclaimer should be returned
    metrics = data['metrics']

    assert metrics['numberOfCases'] == 50
    assert metrics['numberOfSubmitters'] > 0
    assert metrics['numberOfGenes'] > metrics['numberOfUniqueGenes']
    assert metrics['numberOfVariants'] > metrics['numberOfUniqueVariants']
    assert metrics['numberOfFeatures'] > metrics['numberOfUniqueFeatures']
    assert metrics['numberOfCasesWithDiagnosis'] >0
    assert metrics['numberOfUniqueGenesMatched'] == 0 # no gene was provided in match_obj results
    assert metrics['numberOfRequestsReceived'] == 2 # Sent 2 requests
    assert metrics['numberOfPotentialMatchesSent'] == 1 # Just one has returned results


def test_nodes_view(database, test_node, test_client):
    """testing viewing the list of connected nodes as an authenticated client"""

    app.db = database

    # insert a test client in database
    add_node(mongo_db=database, obj=test_client, is_client=True)
    ok_token = test_client['auth_token']

    # If you try to see nodes without being authorized
    response = app.test_client().get('nodes')
    # You should get a not authorized code from server
    assert response.status_code == 401

    # since there are no connected nodes in database
    assert database['nodes'].find().count() == 0
    # When you send an authorized request
    response = app.test_client().get('nodes', headers = auth_headers(ok_token))
    data = json.loads(response.data)
    # you shoud get an empty list
    assert data == []

    # insert a test node in database
    add_node(mongo_db=database, obj=test_node, is_client=False)
    # When you send an authorized request
    response = app.test_client().get('nodes', headers = auth_headers(ok_token))
    data = json.loads(response.data)
    # this time you should get a list with one element
    assert len(data) == 1
    # and the id of the element is the id of the node
    assert data[0]['id'] == test_node['_id']


def test_delete_patient(database, demo_data_path, test_client, match_objs):
    """Test deleting a patient from database by sending a DELETE request"""

    app.db = database
    # load demo data to mock database using function located under utils/load
    inserted_ids = load_demo(demo_data_path, database, app.config.get('MME_HOST'))
    assert len(inserted_ids) == 50 # 50 test cases should be loaded

    # 50 cases present on patients collection
    assert database['patients'].find().count() == 50
    delete_id = 'P0000079'

    # try to delete patient without auth token:
    response = app.test_client().delete(''.join(['patient/delete/', delete_id]))
    assert response.status_code == 401

    # Add a valid client node
    ok_token = test_client['auth_token']
    add_node(mongo_db=app.db, obj=test_client, is_client=True)

    # Send delete request providing a valid token but a non valid id
    response = app.test_client().delete(''.join(['patient/delete/', 'not_a_valid_ID']), headers = auth_headers(ok_token))
    assert response.status_code == 200
    data = json.loads(response.data)
    # but server returns error
    assert data['message'] == 'ERROR. Could not delete a patient with ID not_a_valid_ID from database'

    assert database['matches'].find().count() == 0 # no matches in database
    # insert into database some mock matching objects
    database['matches'].insert_many(match_objs)

    # patient "delete_id" should have two associated matches in database
    assert database['matches'].find({'data.patient.id' : delete_id}).count() == 2

    # Send valid patient ID and valid token
    response = app.test_client().delete(''.join(['patient/delete/', delete_id]), headers = auth_headers(ok_token))
    assert response.status_code == 200

    # make sure that the patient was removed from database
    assert database['patients'].find().count() == 49

    # make sure that patient matches are also gone
    assert database['matches'].find().count() == 1



def test_patient_matches(database, match_objs, test_client):
    """testing the endpoint that retrieves the matchings by patient ID"""

    app.db = database
    # Add a valid client node
    ok_token = test_client['auth_token']
    add_node(mongo_db=app.db, obj=test_client, is_client=True)

    # start from a database with no matches
    assert database['matches'].find().count() == 0
    # import mock matches into datababase
    database['matches'].insert_many(match_objs)
    # database now should have two matching objects

    # test endpoint to get matches by ID
    # test by sending a non-authorized request
    response = app.test_client().get('matches/P0000079')
    # response gives a 401 code (not authorized)
    assert response.status_code == 401

    # try with an authorized request with a used ID that is not in database
    response = app.test_client().get('matches/unknown_patient', headers = auth_headers(ok_token))
    # response gives success
    assert response.status_code == 200
    data = json.loads(response.data)
    # but the patient is not found by server
    assert data['message'] == 'Could not find any matches in database for patient ID unknown_patient'

    # Try with authenticates request and valid patient
    response = app.test_client().get('matches/P0000079', headers = auth_headers(ok_token))
    # response gives success
    assert response.status_code == 200
    data = json.loads(response.data)
    # and there are matches in it
    assert len(data['matches']) == 2 # 2 matches returned because endpoint returns only matches with results

    # Test that there are actually 3 matches by calling directly the function returning matches
    matches = patient_matches(database=database, patient_id='P0000079', type=None, with_results=False)
    assert len(matches) == 3

    # Call the same function to get only external matches
    matches = patient_matches(database=database, patient_id='P0000079', type='external', with_results=False)
    assert len(matches) == 1

    # Call the same function to get only external matches
    matches = patient_matches(database=database, patient_id='P0000079', type='internal', with_results=False)
    assert len(matches) == 2


def test_match(json_patients, test_client, demo_data_path, database):
    """Testing patient matching against patientMatcher database (internal match)"""
    app.db = database

    # add an authorized client to database
    ok_token = test_client['auth_token']
    add_node(mongo_db=app.db, obj=test_client, is_client=True)

    query_patient = {'patient' : json_patients[0]}

    # load demo data in mock database
    inserted_ids = load_demo(demo_data_path, database, app.config.get('MME_HOST'))

    # test the API response validator with non valid patient data:
    malformed_match_results = {'results': 'fakey_results'}
    assert validate_response(malformed_match_results) == 422

    # make sure that there are no patient matches in the 'matches collection'
    assert database['matches'].find().count()==0

    # send a POST request to match patient with patients in database
    response = app.test_client().post('/match', data=json.dumps(query_patient), headers = auth_headers(ok_token))
    assert response.status_code == 200 # POST request should be successful
    data = json.loads(response.data)
    # data should contain results and the max number of results is as defined in the config file
    assert len(data['results']) == app.config['MAX_RESULTS']

    assert type(data['results']) == list # which is a list
    assert 'patient' in data['results'][0] # of patients
    assert 'score' in data['results'][0] # with matching scores

    # make sure that there are match object is created in db for this internal matching
    assert database['matches'].find().count()==1


def test_match_external(test_client, test_node, database, json_patients):
    """Testing the view that is sending post request to trigger matches on external nodes"""
    app.db = database

    # add an authorized client to database
    ok_token = test_client['auth_token']
    add_node(mongo_db=app.db, obj=test_client, is_client=True) # required to trigger external matches

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
    response = app.test_client().post(''.join(['/match/external/', 'not_a_valid_ID']), headers = auth_headers(ok_token))
    # Response is valid
    assert response.status_code == 200
    data = json.loads(response.data)
    # but server returns error
    assert data['message'] == 'ERROR. Could not find any patient with ID not_a_valid_ID in database'

    # there are no matches in mock database
    assert database['matches'].find().count() == 0
    # after sending an authorized request with a patient ID that exists on database

    # Check that external matching doesn't work if there are no connected nodes:
    response = app.test_client().post(''.join(['/match/external/', inserted_id]), headers = auth_headers(ok_token))
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'Could not find any other node connected to this MatchMaker server'

    # Try to send a request for a match on a node that does not exist
    response = app.test_client().post(''.join(['/match/external/', inserted_id, '?node=meh']), headers = auth_headers(ok_token))
    assert response.status_code == 200
    data = json.loads(response.data)
    # And check that node not found is in response message
    assert data['message'] == 'ERROR. Could not find any connected node with id meh in database'

    # insert a connected node
    add_node(mongo_db=app.db, obj=test_node, is_client=False) # required for external matches
    # send a request to match patients against all nodes
    response = app.test_client().post(''.join(['/match/external/', inserted_id]), headers = auth_headers(ok_token))

    # Response should be valid
    assert response.status_code == 200
    # And a new match should be created in matches collection
    assert database['matches'].find().count() == 1

    # send a request to match patients against the specific existing node:
    response = app.test_client().post(''.join(['/match/external/', inserted_id, '?node=', test_node['_id']]), headers = auth_headers(ok_token))
    # Response should be valid
    assert response.status_code == 200

    # And a new match should be created in matches collection. So total matches are 2
    assert database['matches'].find().count() == 2


def unauth_headers():
    head = {
        'Content-Type': 'application/vnd.ga4gh.matchmaker.v1.0+json',
        'Accept': ['application/vnd.ga4gh.matchmaker.v1.0+json', 'application/json'],
        'X-Auth-Token': 'wrong_token'
    }
    return head

def auth_headers(test_token):
    head = {
        'Content-Type': 'application/vnd.ga4gh.matchmaker.v1.0+json',
        'Accept': ['application/vnd.ga4gh.matchmaker.v1.0+json', 'application/json'],
        'X-Auth-Token': test_token
    }
    return head
