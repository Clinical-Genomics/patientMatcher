# -*- coding: utf-8 -*-
import json

import responses
from patientMatcher.__version__ import __version__
from patientMatcher.match.handler import patient_matches
from patientMatcher.parse.patient import mme_patient
from patientMatcher.server.controllers import validate_response
from patientMatcher.utils.add import add_node, backend_add_patient, load_demo_patients


def test_heartbeat(mock_app, database, test_client):
    """Test sending a GET request to see if app has a heartbeat"""

    # send a get request without being authorized
    response = mock_app.test_client().get("heartbeat")
    assert response.status_code == 401

    # add an authorized client to database
    ok_token = test_client["auth_token"]
    add_node(mongo_db=mock_app.db, obj=test_client, is_client=True)

    # make sure that the request using its token is valid
    response = mock_app.test_client().get("heartbeat", headers=auth_headers(ok_token))
    assert response.status_code == 200

    # Make sure that all important info is returned
    data = json.loads(response.data)
    assert data["disclaimer"] == mock_app.config.get("DISCLAIMER")
    assert data["heartbeat"]["version"] == __version__
    assert data["heartbeat"]["production"] is False
    assert isinstance(data["heartbeat"]["accept"], list)
    assert len(data["heartbeat"]["accept"]) > 0


def test_add_patient_no_auth(mock_app, gpx4_patients):
    """Test sending a POST request to server to add a patient without valid token"""

    assert len(gpx4_patients) == 2  # patients with variants in this gene
    patient_data = gpx4_patients[1]

    # try to add a patient without being authorized
    response = mock_app.test_client().post(
        "patient/add", data=json.dumps(patient_data), headers=unauth_headers()
    )
    assert response.status_code == 401


def test_add_patient_malformed_patient(mock_app, test_client, gpx4_patients, test_node):
    """Test sending a POST request to server to add a patient with malformed patient json"""

    patient_data = gpx4_patients[1]

    # Given a node with authorized token
    ok_token = test_client["auth_token"]

    add_node(mongo_db=mock_app.db, obj=test_client, is_client=True)
    add_node(mongo_db=mock_app.db, obj=test_node, is_client=False)  #

    # send a malformed json object using a valid auth token
    malformed_json = "{'_id': 'patient_id' }"
    response = mock_app.test_client().post(
        "patient/add", data=malformed_json, headers=auth_headers(ok_token)
    )
    # and check that you get the correct error code from server(400)
    assert response.status_code == 400


def test_add_patient_malformed_data(mock_app, test_client, gpx4_patients, test_node):
    """Test sending a POST request to server to add a patient with malformed data"""

    patient_data = gpx4_patients[1]

    # Given a node with authorized token
    ok_token = test_client["auth_token"]

    add_node(mongo_db=mock_app.db, obj=test_client, is_client=True)
    add_node(
        mongo_db=mock_app.db, obj=test_node, is_client=False
    )  # add a test node, to perform external matching

    # add a patient not conforming to MME API using a valid auth token
    response = mock_app.test_client().post(
        "patient/add", data=json.dumps(patient_data), headers=auth_headers(ok_token)
    )
    # and check that the server returns an error 422 (unprocessable entity)
    assert response.status_code == 422


@responses.activate
def test_add_patient(mock_app, test_client, gpx4_patients, test_node, database):
    """Test adding a patient by sending a POST request to the add endpoint with valid data"""

    # GIVEN a mocked Ensembl REST API converting gene symbol to Ensembl ID
    responses.add(
        responses.GET,
        f"https://grch37.rest.ensembl.org/xrefs/symbol/homo_sapiens/GPX4?external_db=HGNC",
        json=[{"id": "ENSG00000167468", "type": "gene"}],
        status=200,
    )

    patient_data = gpx4_patients[1]

    # Given a node with authorized token
    ok_token = test_client["auth_token"]

    add_node(mongo_db=mock_app.db, obj=test_client, is_client=True)
    add_node(
        mongo_db=mock_app.db, obj=test_node, is_client=False
    )  # add a test node, to perform external matching

    # a matches collection without documents
    assert database["matches"].find_one() is None

    # and an empty patients collection
    assert database["patients"].find_one() is None

    patient_obj = {"patient": patient_data}  # this is a valid patient object
    # WHEN the patient is added using the add enpoint
    response = mock_app.test_client().post(
        "patient/add", data=json.dumps(patient_obj), headers=auth_headers(ok_token)
    )
    assert response.status_code == 200

    # make sure that the POST request to add the patient triggers the matching request to an external node
    assert database["matches"].find_one()

    # There should be one patient in database now
    assert database["patients"].find_one()

    # the patient in database has label "Patient number 1"
    result = database["patients"].find_one({"label": "350_2-test"})
    # make sure patient's gene was converted to ensembl
    assert result["genomicFeatures"][0]["gene"]["id"].startswith("ENSG")
    # and that non-standard but informative _geneName field was added to genomic feature
    assert result["genomicFeatures"][0]["gene"]["_geneName"] == "GPX4"


def test_update_patient(mock_app, test_client, gpx4_patients, test_node, database):
    """Test updating a patient by sending a POST request to the add endpoint with valid data"""

    patient_data = gpx4_patients[1]
    # Modify patient's contact href with a simple email
    patient_data["contact"]["href"] = "somebody@test.se"

    # Given a node with authorized token
    ok_token = test_client["auth_token"]

    add_node(mongo_db=mock_app.db, obj=test_client, is_client=True)
    add_node(
        mongo_db=mock_app.db, obj=test_node, is_client=False
    )  # add a test node, to perform external matching

    # a matches collection without documents
    assert database["matches"].find_one() is None

    # and an empty patients collection
    assert database["patients"].find_one() is None

    # GIVEN a patient added using the add enpoint
    patient_obj = {"patient": patient_data}  # this is a valid patient object
    response = mock_app.test_client().post(
        "patient/add", data=json.dumps(patient_obj), headers=auth_headers(ok_token)
    )
    assert response.status_code == 200

    # WHEN the patient is updated using the same add endpoint
    patient_data["label"] = "modified patient label"
    patient_obj = {"patient": patient_data}  # this
    response = mock_app.test_client().post(
        "patient/add", data=json.dumps(patient_obj), headers=auth_headers(ok_token)
    )
    assert response.status_code == 200

    # Then there should still be one patient in the database
    updated_patient = database["patients"].find_one()
    # With an updated and valid email address
    assert updated_patient["contact"]["href"] == "mailto:somebody@test.se"

    # And the update has triggered an additional external patient matching
    results = database["matches"].find()
    assert len(list(results)) == 2


def test_metrics(mock_app, database, test_client, demo_data_path, match_objs):
    """Testing viewing the list of patients on server for authorized users"""

    # load demo data of 50 test patients
    inserted_ids = load_demo_patients(demo_data_path, database)
    assert len(inserted_ids) == 50  # 50 test cases should be loaded

    # load mock matches into database
    database.matches.insert_many(match_objs)
    results = database.matches.find()
    assert len(list(results)) == 3

    # send a get request without being authorized
    response = mock_app.test_client().get("metrics")
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data["disclaimer"]  # disclaimer should be returned
    metrics = data["metrics"]

    assert metrics["numberOfCases"] == 50
    assert metrics["numberOfSubmitters"] > 0
    assert metrics["numberOfGenes"] > metrics["numberOfUniqueGenes"]
    assert metrics["numberOfVariants"] > metrics["numberOfUniqueVariants"]
    assert metrics["numberOfFeatures"] > metrics["numberOfUniqueFeatures"]
    assert metrics["numberOfCasesWithDiagnosis"] > 0
    assert metrics["numberOfUniqueGenesMatched"] == 0  # no gene was provided in match_obj results
    assert metrics["numberOfRequestsReceived"] == 2  # Sent 2 requests
    assert metrics["numberOfPotentialMatchesSent"] == 1  # Just one has returned results


def test_nodes_view(mock_app, database, test_node, test_client):
    """testing viewing the list of connected nodes as an authenticated client"""

    # insert a test client in database
    add_node(mongo_db=database, obj=test_client, is_client=True)
    ok_token = test_client["auth_token"]

    # If you try to see nodes without being authorized
    response = mock_app.test_client().get("nodes")
    # You should get a not authorized code from server
    assert response.status_code == 401

    # since there are no connected nodes in database
    assert database["nodes"].find_one() is None
    # When you send an authorized request
    response = mock_app.test_client().get("nodes", headers=auth_headers(ok_token))
    data = json.loads(response.data)
    # you shoud get an empty list
    assert data == []

    # insert a test node in database
    add_node(mongo_db=database, obj=test_node, is_client=False)
    # When you send an authorized request
    response = mock_app.test_client().get("nodes", headers=auth_headers(ok_token))
    data = json.loads(response.data)
    # this time you should get a list with one element
    assert len(data) == 1
    # and the id of the element is the id of the node
    assert data[0]["id"] == test_node["_id"]


def test_delete_patient(mock_app, database, gpx4_patients, test_client, match_objs):
    """Test deleting a patient from database by sending a DELETE request"""

    # load 2 patients from demo data in mock database
    assert len(gpx4_patients) == 2
    inserted_ids = []
    for pat in gpx4_patients:
        # convert patient in mme patient type (convert also gene to ensembl)
        mme_pat = mme_patient(pat, True)
        inserted_ids.append(backend_add_patient(database, mme_pat))

    assert len(inserted_ids) == 2

    # 50 cases present on patients collection
    delete_id = "P0001058"

    # try to delete patient without auth token:
    response = mock_app.test_client().delete("".join(["patient/delete/", delete_id]))
    assert response.status_code == 401

    # Add a valid client node
    ok_token = test_client["auth_token"]
    add_node(mongo_db=mock_app.db, obj=test_client, is_client=True)

    # Send delete request providing a valid token but a non valid id
    response = mock_app.test_client().delete(
        "".join(["patient/delete/", "not_a_valid_ID"]), headers=auth_headers(ok_token)
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    # but server returns error
    assert (
        data["message"] == "ERROR. Could not delete a patient with ID not_a_valid_ID from database"
    )

    assert database["matches"].find_one() is None  # no matches in database
    # insert into database some mock matching objects
    database["matches"].insert_many(match_objs)

    # patient "delete_id" should have two associated matches in database
    results = database["matches"].find({"data.patient.id": delete_id})
    assert len(list(results)) == 2

    # Send valid patient ID and valid token
    response = mock_app.test_client().delete(
        "".join(["patient/delete/", delete_id]), headers=auth_headers(ok_token)
    )
    assert response.status_code == 200

    # make sure that the patient was removed from database
    results = database["patients"].find()
    assert len(list(results)) == 1

    # make sure that patient matches are also gone
    results = database["matches"].find()
    assert len(list(results)) == 1


def test_patient_matches(mock_app, database, match_objs, test_client):
    """testing the endpoint that retrieves the matchings by patient ID"""

    # Add a valid client node
    ok_token = test_client["auth_token"]
    add_node(mongo_db=mock_app.db, obj=test_client, is_client=True)

    # start from a database with no matches
    assert database["matches"].find_one() is None
    # import mock matches into datababase
    database["matches"].insert_many(match_objs)
    # database now should have two matching objects

    # test endpoint to get matches by ID
    # test by sending a non-authorized request
    response = mock_app.test_client().get("matches/P0001058")
    # response gives a 401 code (not authorized)
    assert response.status_code == 401

    # try with an authorized request with a used ID that is not in database
    response = mock_app.test_client().get("matches/unknown_patient", headers=auth_headers(ok_token))
    # response gives success
    assert response.status_code == 200
    data = json.loads(response.data)
    # but the patient is not found by server
    assert (
        data["message"] == "Could not find any matches in database for patient ID unknown_patient"
    )

    # Try with authenticates request and valid patient
    response = mock_app.test_client().get("matches/P0001058", headers=auth_headers(ok_token))
    # response gives success
    assert response.status_code == 200
    data = json.loads(response.data)
    # and there are matches in it
    assert (
        len(data["matches"]) == 2
    )  # 2 matches returned because endpoint returns only matches with results

    # Test that there are actually 3 matches by calling directly the function returning matches
    matches = patient_matches(
        database=database, patient_id="P0001058", type=None, with_results=False
    )
    assert len(matches) == 3
    for match in matches:
        for result in match["results"]:
            for patient in result["patients"]:
                assert patient["patient"]["id"]

    # Call the same function to get only external matches
    matches = patient_matches(
        database=database, patient_id="P0001058", type="external", with_results=False
    )
    assert len(matches) == 1

    # Call the same function to get only external matches
    matches = patient_matches(
        database=database, patient_id="P0001058", type="internal", with_results=False
    )
    assert len(matches) == 2


@responses.activate
def test_match_hgnc_symbol_patient(mock_app, gpx4_patients, test_client, database):
    """Testing matching patient with gene symbol against patientMatcher database (internal matching)"""

    # GIVEN a mocked Ensembl REST API converting gene symbol to Ensembl ID
    responses.add(
        responses.GET,
        f"https://grch37.rest.ensembl.org/xrefs/symbol/homo_sapiens/GPX4?external_db=HGNC",
        json=[{"id": "ENSG00000167468", "type": "gene"}],
        status=200,
    )

    # GIVEN a mocked Ensembl gene lookup service:
    responses.add(
        responses.GET,
        f"https://grch37.rest.ensembl.org/lookup/id/ENSG00000167468",
        json=[{"display_name": "GPX4"}],
        status=200,
    )

    # GIVEN a mocked liftover service:
    responses.add(
        responses.GET,
        f"https://grch37.rest.ensembl.org/map/human/GRCh37/19:1105813..1105814/GRCh38?content-type=application/json",
        json=[],
        status=200,
    )
    responses.add(
        responses.GET,
        f"https://grch37.rest.ensembl.org/map/human/GRCh37/19:1106232..1106238/GRCh38?content-type=application/json",
        json=[],
        status=200,
    )

    # add an authorized client to database
    ok_token = test_client["auth_token"]
    add_node(mongo_db=mock_app.db, obj=test_client, is_client=True)

    query_patient = {"patient": gpx4_patients[0]}
    assert query_patient["patient"]["genomicFeatures"][0]["gene"]["id"] == "GPX4"

    # load 2 test patient in mock database
    assert len(gpx4_patients) == 2
    inserted_ids = []
    for pat in gpx4_patients:
        # convert patient in mme patient type (convert also gene to ensembl)
        mme_pat = mme_patient(pat, True)
        inserted_ids.append(backend_add_patient(database, mme_pat))

    assert len(inserted_ids) == 2

    # test the API response validator with non valid patient data:
    malformed_match_results = {"results": "fakey_results"}
    assert validate_response(malformed_match_results) == 422

    # make sure that there are no patient matches in the 'matches collection'
    assert database["matches"].find_one() is None

    # send a POST request to match patient with patients in database
    response = mock_app.test_client().post(
        "/match", data=json.dumps(query_patient), headers=auth_headers(ok_token)
    )
    assert response.status_code == 200  # POST request should be successful
    data = json.loads(response.data)
    # data should contain results and the max number of results is as defined in the config file
    assert len(data["results"]) == 2
    assert type(data["results"]) == list  # which is a list
    assert "patient" in data["results"][0]  # of patients
    assert "score" in data["results"][0]  # with matching scores
    assert "contact" in data["results"][0]["patient"]  # contact info should be available as well

    # make sure that there are match object is created in db for this internal matching
    match = database["matches"].find_one()
    for res in match["results"]:
        for pat in res["patients"]:
            assert pat["patient"]["contact"]  # each result should have a contact person
            assert pat["score"]["patient"] > 0


@responses.activate
def test_match_ensembl_patient(mock_app, test_client, gpx4_patients, database):
    """Test matching patient with ensembl gene against patientMatcher database (internal matching)"""

    # GIVEN a mocked Ensembl REST API converting gene symbol to Ensembl ID
    responses.add(
        responses.GET,
        f"https://grch37.rest.ensembl.org/xrefs/symbol/homo_sapiens/GPX4?external_db=HGNC",
        json=[{"id": "ENSG00000167468", "type": "gene"}],
        status=200,
    )

    # GIVEN a mocked Ensembl gene lookup service:
    responses.add(
        responses.GET,
        f"https://grch37.rest.ensembl.org/lookup/id/ENSG00000167468",
        json=[{"display_name": "GPX4"}],
        status=200,
    )

    # GIVEN a mocked liftover service:
    responses.add(
        responses.GET,
        f"https://grch37.rest.ensembl.org/map/human/GRCh37/19:1105813..1105814/GRCh38?content-type=application/json",
        json=[],
        status=200,
    )
    responses.add(
        responses.GET,
        f"https://grch37.rest.ensembl.org/map/human/GRCh37/19:1106232..1106238/GRCh38?content-type=application/json",
        json=[],
        status=200,
    )

    # add an authorized client to database
    ok_token = test_client["auth_token"]
    add_node(mongo_db=mock_app.db, obj=test_client, is_client=True)

    query_patient = {"patient": mme_patient(gpx4_patients[0], True)}
    assert query_patient["patient"]["genomicFeatures"][0]["gene"]["id"].startswith("ENSG")

    # load 2 test patient in mock database
    assert len(gpx4_patients) == 2
    inserted_ids = []
    for pat in gpx4_patients:
        # convert patient in mme patient type (convert also gene to ensembl)
        mme_pat = mme_patient(pat, True)
        inserted_ids.append(backend_add_patient(database, mme_pat))

    assert len(inserted_ids) == 2

    # make sure that there are no patient matches in the 'matches collection'
    assert database["matches"].find_one() is None

    # send a POST request to match patient with patients in database
    response = mock_app.test_client().post(
        "/match", data=json.dumps(query_patient), headers=auth_headers(ok_token)
    )
    assert response.status_code == 200  # POST request should be successful
    data = json.loads(response.data)
    # data should contain results and the max number of results is as defined in the config file
    assert len(data["results"]) == 2
    assert type(data["results"]) == list  # which is a list
    assert "patient" in data["results"][0]  # of patients
    assert "score" in data["results"][0]  # with matching scores
    assert "contact" in data["results"][0]["patient"]  # contact info should be available as well

    # make sure that a match object is created in db for this internal matching
    match = database["matches"].find_one()
    for res in match["results"]:
        for pat in res["patients"]:
            assert pat["patient"]["contact"]  # each result should have a contact person
            assert pat["score"]["patient"] > 0
    # and query patient should have hgnc gene symbol saved as non-standard _geneName field
    assert match["data"]["patient"]["genomicFeatures"][0]["gene"]["_geneName"] == "GPX4"


@responses.activate
def test_match_entrez_patient(mock_app, test_client, gpx4_patients, database):
    """Test matching patient with ensembl gene against patientMatcher database (internal matching)"""

    # GIVEN a mocked Ensembl REST API converting gene symbol to Ensembl ID
    responses.add(
        responses.GET,
        f"https://grch37.rest.ensembl.org/xrefs/symbol/homo_sapiens/GPX4?external_db=HGNC",
        json=[{"id": "ENSG00000167468", "type": "gene"}],
        status=200,
    )

    # GIVEN a mocked Ensembl gene lookup service:
    responses.add(
        responses.GET,
        f"https://grch37.rest.ensembl.org/lookup/id/ENSG00000167468",
        json=[{"display_name": "GPX4"}],
        status=200,
    )

    # GIVEN a mocked liftover service:
    responses.add(
        responses.GET,
        f"https://grch37.rest.ensembl.org/map/human/GRCh37/19:1105813..1105814/GRCh38?content-type=application/json",
        json=[],
        status=200,
    )
    responses.add(
        responses.GET,
        f"https://grch37.rest.ensembl.org/map/human/GRCh37/19:1106232..1106238/GRCh38?content-type=application/json",
        json=[],
        status=200,
    )

    # add an authorized client to database
    ok_token = test_client["auth_token"]
    add_node(mongo_db=mock_app.db, obj=test_client, is_client=True)

    query_patient = gpx4_patients[0]
    query_patient = {"patient": gpx4_patients[0]}
    for feat in query_patient["patient"]["genomicFeatures"]:
        feat["gene"]["id"] == "2879"  # entrez id for GPX4

    # load 2 test patient in mock database
    assert len(gpx4_patients) == 2
    inserted_ids = []
    for pat in gpx4_patients:
        # convert patient in mme patient type (convert also gene to ensembl)
        mme_pat = mme_patient(pat, True)
        inserted_ids.append(backend_add_patient(database, mme_pat))

    assert len(inserted_ids) == 2

    # make sure that there are no patient matches in the 'matches collection'
    assert database["matches"].find_one() is None

    # send a POST request to match patient with patients in database
    response = mock_app.test_client().post(
        "/match", data=json.dumps(query_patient), headers=auth_headers(ok_token)
    )
    assert response.status_code == 200  # POST request should be successful
    data = json.loads(response.data)
    # data should contain results and the max number of results is as defined in the config file
    assert len(data["results"]) == 2
    assert type(data["results"]) == list  # which is a list
    assert "patient" in data["results"][0]  # of patients
    assert "score" in data["results"][0]  # with matching scores
    assert "contact" in data["results"][0]["patient"]  # contact info should be available as well

    # make sure that a match object is created in db for this internal matching
    match = database["matches"].find_one()
    for res in match["results"]:
        for pat in res["patients"]:
            assert pat["patient"]["contact"]  # each result should have a contact person
            assert pat["score"]["patient"] > 0
    # and query patient should have hgnc gene symbol saved as non-standard _geneName field
    assert match["data"]["patient"]["genomicFeatures"][0]["gene"]["_geneName"] == "GPX4"


def test_match_external(mock_app, test_client, test_node, database, json_patients):
    """Testing the view that is sending post request to trigger matches on external nodes"""

    # add an authorized client to database
    ok_token = test_client["auth_token"]
    add_node(
        mongo_db=mock_app.db, obj=test_client, is_client=True
    )  # required to trigger external matches

    a_patient = json_patients[0]
    parsed_patient = mme_patient(a_patient)

    # insert patient into mock database:
    assert database["patients"].find_one() is None
    inserted_id = database["patients"].insert_one(parsed_patient).inserted_id
    assert database["patients"].find_one()

    # send an un-authorized match request to server
    response = mock_app.test_client().post("".join(["/match/external/", inserted_id]))
    # server should return 401 (not authorized)
    assert response.status_code == 401

    # send an authorized request with a patient ID that doesn't exist on server:
    response = mock_app.test_client().post(
        "".join(["/match/external/", "not_a_valid_ID"]), headers=auth_headers(ok_token)
    )
    # Response is valid
    assert response.status_code == 200
    data = json.loads(response.data)
    # but server returns error
    assert data["message"] == "ERROR. Could not find any patient with ID not_a_valid_ID in database"

    # there are no matches in mock database
    assert database["matches"].find_one() is None
    # after sending an authorized request with a patient ID that exists on database

    # Check that external matching doesn't work if there are no connected nodes:
    response = mock_app.test_client().post(
        "".join(["/match/external/", inserted_id]), headers=auth_headers(ok_token)
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["message"] == "Could not find any other node connected to this MatchMaker server"

    # Try to send a request for a match on a node that does not exist
    response = mock_app.test_client().post(
        "".join(["/match/external/", inserted_id, "?node=meh"]), headers=auth_headers(ok_token)
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    # And check that node not found is in response message
    assert data["message"] == "ERROR. Could not find any connected node with id meh in database"

    # insert a connected node
    add_node(mongo_db=mock_app.db, obj=test_node, is_client=False)  # required for external matches
    # send a request to match patients against all nodes
    response = mock_app.test_client().post(
        "".join(["/match/external/", inserted_id]), headers=auth_headers(ok_token)
    )

    # Response should be valid
    assert response.status_code == 200
    # And a new match should be created in matches collection
    assert database["matches"].find_one()

    # send a request to match patients against the specific existing node:
    response = mock_app.test_client().post(
        "".join(["/match/external/", inserted_id, "?node=", test_node["_id"]]),
        headers=auth_headers(ok_token),
    )
    # Response should be valid
    assert response.status_code == 200

    # And a new match should be created in matches collection. So total matches are 2
    results = database["matches"].find()
    assert len(list(results)) == 2


def unauth_headers():
    head = {
        "Content-Type": "application/vnd.ga4gh.matchmaker.v1.0+json",
        "Accept": ["application/vnd.ga4gh.matchmaker.v1.0+json", "application/json"],
        "X-Auth-Token": "wrong_token",
    }
    return head


def auth_headers(test_token):
    head = {
        "Content-Type": "application/vnd.ga4gh.matchmaker.v1.0+json",
        "Accept": ["application/vnd.ga4gh.matchmaker.v1.0+json", "application/json"],
        "X-Auth-Token": test_token,
    }
    return head
