# -*- coding: utf-8 -*-
import json

import responses

from patientMatcher.__version__ import __version__
from patientMatcher.match.handler import patient_matches
from patientMatcher.parse.patient import mme_patient
from patientMatcher.server.controllers import validate_response
from patientMatcher.utils.add import add_node, backend_add_patient, load_demo_patients

ADD_PATIENT_ENDPOINT = "patient/add"
DELETE_PATIENT_ENDPOINT = "patient/delete/"
MATCH_ENDPOINT = "/match"
MATCH_EXTERNAL_ENDPOINT = "/match/external/"
CONTENT_TYPE = "application/vnd.ga4gh.matchmaker.v1.0+json"


def _setup(mock_app, test_client, test_node, database):
    # common setup used in all tests
    ok_token = test_client["auth_token"]

    add_node(mongo_db=mock_app.db, obj=test_client, is_client=True)
    add_node(mongo_db=mock_app.db, obj=test_node, is_client=False)

    assert database["matches"].find_one() is None
    assert database["patients"].find_one() is None

    return ok_token


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
        ADD_PATIENT_ENDPOINT, data=json.dumps(patient_data), headers=unauth_headers()
    )
    assert response.status_code == 401


def test_add_patient_malformed_patient(mock_app, test_client, gpx4_patients, test_node, database):
    """Test sending a POST request to server to add a patient with malformed patient json"""

    ok_token = _setup(mock_app, test_client, test_node, database)

    malformed_json = "{'_id': 'patient_id' }"

    response = mock_app.test_client().post(
        ADD_PATIENT_ENDPOINT,
        data=malformed_json,
        headers=auth_headers(ok_token),
    )

    assert response.status_code == 400


def test_add_patient_malformed_data(mock_app, test_client, gpx4_patients, test_node, database):
    """Test sending a POST request to server to add a patient with malformed data"""

    patient_data = gpx4_patients[1]

    ok_token = _setup(mock_app, test_client, test_node, database)

    response = mock_app.test_client().post(
        ADD_PATIENT_ENDPOINT,
        data=json.dumps(patient_data),
        headers=auth_headers(ok_token),
    )

    assert response.status_code == 422


@responses.activate
def test_add_patient_from_demo_data(
    mock_app, test_client, gpx4_patients, test_node, database, mocked_ensemble_responses
):
    patient_data = gpx4_patients[1]
    ok_token = _setup(mock_app, test_client, test_node, database)

    response = mock_app.test_client().post(
        ADD_PATIENT_ENDPOINT,
        data=json.dumps({"patient": patient_data}),
        headers=auth_headers(ok_token),
    )
    assert response.status_code == 200

    assert database["matches"].find_one()
    assert database["patients"].find_one()

    result = database["patients"].find_one({"label": "350_2-test"})
    gene = result["genomicFeatures"][0]["gene"]

    assert gene["id"].startswith("ENSG")
    assert gene["_geneName"] == "GPX4"


@responses.activate
def test_add_one_patient_with_additional_contacts(
    mock_app, test_client, entrez_gene_patient, test_node, database, mocked_ensemble_responses
):
    patient_data = entrez_gene_patient
    ok_token = _setup(mock_app, test_client, test_node, database)

    response = mock_app.test_client().post(
        ADD_PATIENT_ENDPOINT,
        data=json.dumps({"patient": patient_data}),
        headers=auth_headers(ok_token),
    )
    assert response.status_code == 200

    assert database["matches"].find_one()

    result = database["patients"].find_one()
    assert result["additionalContacts"]


def test_update_patient(mock_app, test_client, gpx4_patients, test_node, database):
    patient_data = gpx4_patients[1]
    patient_data["contact"]["href"] = "somebody@test.se"

    ok_token = _setup(mock_app, test_client, test_node, database)

    # initial add
    response = mock_app.test_client().post(
        ADD_PATIENT_ENDPOINT,
        data=json.dumps({"patient": patient_data}),
        headers=auth_headers(ok_token),
    )
    assert response.status_code == 200

    # update
    patient_data["label"] = "modified patient label"
    response = mock_app.test_client().post(
        ADD_PATIENT_ENDPOINT,
        data=json.dumps({"patient": patient_data}),
        headers=auth_headers(ok_token),
    )
    assert response.status_code == 200

    updated_patient = database["patients"].find_one()

    assert updated_patient["contact"]["href"] == "mailto:somebody@test.se"

    results = list(database["matches"].find())
    assert len(results) == 2


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

    ok_token = _setup(mock_app, test_client, test_node, database)

    # Clear nodes added by _setup to preserve original test logic
    database["nodes"].delete_many({})

    # Unauthorized request
    response = mock_app.test_client().get("nodes")
    assert response.status_code == 401

    # No nodes in database
    assert database["nodes"].find_one() is None

    # Add only client (as in original test)
    add_node(mongo_db=database, obj=test_client, is_client=True)

    # Authorized request → empty list
    response = mock_app.test_client().get("nodes", headers=auth_headers(ok_token))
    data = json.loads(response.data)
    assert data == []

    # Add a test node
    add_node(mongo_db=database, obj=test_node, is_client=False)

    # Authorized request → one node
    response = mock_app.test_client().get("nodes", headers=auth_headers(ok_token))
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]["id"] == test_node["_id"]


def test_delete_patient(mock_app, database, gpx4_patients, test_client, test_node, match_objs):
    """Test deleting a patient from database by sending a DELETE request"""

    # GIVEN 2 patients already exist in DB
    assert len(gpx4_patients) == 2

    for pat in gpx4_patients:
        mme_pat = mme_patient(pat, True)
        backend_add_patient(database, mme_pat)

    delete_id = "P0001058"

    # WHEN deleting without auth
    response = mock_app.test_client().delete(DELETE_PATIENT_ENDPOINT + delete_id)
    assert response.status_code == 401

    # GIVEN an authorized client node
    ok_token = test_client["auth_token"]
    add_node(mongo_db=mock_app.db, obj=test_client, is_client=True)

    # WHEN deleting with invalid patient ID
    response = mock_app.test_client().delete(
        DELETE_PATIENT_ENDPOINT + "not_a_valid_ID",
        headers=auth_headers(ok_token),
    )
    assert response.status_code == 200

    data = json.loads(response.data)
    assert (
        data["message"] == "ERROR. Could not delete a patient with ID not_a_valid_ID from database"
    )

    # ensure no matches initially
    assert database["matches"].find_one() is None

    # insert mock matches
    database["matches"].insert_many(match_objs)

    # ensure correct match count before deletion
    results = database["matches"].find({"data.patient.id": delete_id})
    assert len(list(results)) == 2

    # WHEN deleting valid patient
    response = mock_app.test_client().delete(
        DELETE_PATIENT_ENDPOINT + delete_id,
        headers=auth_headers(ok_token),
    )
    assert response.status_code == 200

    # THEN patient should be removed
    assert len(list(database["patients"].find({}))) == 1

    # AND related matches should be cleaned up
    assert len(list(database["matches"].find({}))) == 1


def test_patient_matches(mock_app, database, match_objs, test_client, test_node):
    """testing the endpoint that retrieves the matchings by patient ID"""

    # Setup authorized client and node
    ok_token = _setup(mock_app, test_client, test_node, database)

    # start from a database with no matches
    assert database["matches"].find_one() is None

    # import mock matches into database
    database["matches"].insert_many(match_objs)

    # unauthorized request
    response = mock_app.test_client().get("matches/P0001058")
    assert response.status_code == 401

    # authorized request with unknown patient
    response = mock_app.test_client().get(
        "matches/unknown_patient",
        headers=auth_headers(ok_token),
    )
    assert response.status_code == 200

    data = json.loads(response.data)
    assert (
        data["message"] == "Could not find any matches in database for patient ID unknown_patient"
    )

    # authorized request with valid patient
    response = mock_app.test_client().get(
        "matches/P0001058",
        headers=auth_headers(ok_token),
    )
    assert response.status_code == 200

    data = json.loads(response.data)
    assert len(data["matches"]) == 2  # only matches with results returned

    # direct function: all matches
    matches = patient_matches(
        database=database,
        patient_id="P0001058",
        type=None,
        with_results=False,
    )
    assert len(matches) == 3

    for match in matches:
        for result in match["results"]:
            for patient in result["patients"]:
                assert patient["patient"]["id"]

    # external matches only
    matches = patient_matches(
        database=database,
        patient_id="P0001058",
        type="external",
        with_results=False,
    )
    assert len(matches) == 1

    # internal matches only
    matches = patient_matches(
        database=database,
        patient_id="P0001058",
        type="internal",
        with_results=False,
    )
    assert len(matches) == 2


@responses.activate
def test_match_hgnc_symbol_patient(
    mock_app, gpx4_patients, test_client, test_node, database, mocked_ensemble_responses
):
    """Testing matching patient with gene symbol against patientMatcher database (internal matching)"""

    # Setup authorized client and node
    ok_token = _setup(mock_app, test_client, test_node, database)

    query_patient = {"patient": gpx4_patients[0]}
    assert query_patient["patient"]["genomicFeatures"][0]["gene"]["id"] == "GPX4"

    # Load 2 test patients into mock database
    assert len(gpx4_patients) == 2
    inserted_ids = []
    for pat in gpx4_patients:
        mme_pat = mme_patient(pat, True)
        inserted_ids.append(backend_add_patient(database, mme_pat))
    assert len(inserted_ids) == 2

    # Validate API response validator
    malformed_match_results = {"results": "fakey_results"}
    assert validate_response(malformed_match_results) == 422

    # Ensure no matches exist initially
    assert database["matches"].find_one() is None

    # Send match request
    response = mock_app.test_client().post(
        MATCH_ENDPOINT,
        data=json.dumps(query_patient),
        headers=auth_headers(ok_token),
    )
    assert response.status_code == 200

    data = json.loads(response.data)
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 2
    assert "patient" in data["results"][0]
    assert "score" in data["results"][0]
    assert "contact" in data["results"][0]["patient"]

    # Verify DB match object
    match = database["matches"].find_one()
    for res in match["results"]:
        for pat in res["patients"]:
            assert pat["patient"]["contact"]
            assert pat["score"]["patient"] > 0


@responses.activate
def test_match_ensembl_patient(
    mock_app, test_client, gpx4_patients, test_node, database, mocked_ensemble_responses
):
    """Test matching patient with Ensembl gene against patientMatcher database (internal matching)"""

    # Setup authorized client + node
    ok_token = _setup(mock_app, test_client, test_node, database)

    query_patient = {"patient": mme_patient(gpx4_patients[0], True)}
    assert query_patient["patient"]["genomicFeatures"][0]["gene"]["id"].startswith("ENSG")

    assert len(gpx4_patients) == 2
    inserted_ids = []
    for pat in gpx4_patients:
        mme_pat = mme_patient(pat, True)
        inserted_ids.append(backend_add_patient(database, mme_pat))
    assert len(inserted_ids) == 2

    assert database["matches"].find_one() is None

    response = mock_app.test_client().post(
        MATCH_ENDPOINT,
        data=json.dumps(query_patient),
        headers=auth_headers(ok_token),
    )
    assert response.status_code == 200

    data = json.loads(response.data)
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 2
    assert "patient" in data["results"][0]
    assert "score" in data["results"][0]
    assert "contact" in data["results"][0]["patient"]

    match = database["matches"].find_one()
    for res in match["results"]:
        for pat in res["patients"]:
            assert pat["patient"]["contact"]
            assert pat["score"]["patient"] > 0

    assert match["data"]["patient"]["genomicFeatures"][0]["gene"]["_geneName"] == "GPX4"


@responses.activate
def test_match_entrez_patient(mock_app, test_client, gpx4_patients, test_node, database):
    """Test matching patient with Ensembl gene against patientMatcher database (internal matching)"""

    # Mock Ensembl services
    responses.add(
        responses.GET,
        "https://grch37.rest.ensembl.org/xrefs/symbol/homo_sapiens/GPX4?external_db=HGNC",
        json=[{"id": "ENSG00000167468", "type": "gene"}],
        status=200,
    )

    responses.add(
        responses.GET,
        "https://grch37.rest.ensembl.org/lookup/id/ENSG00000167468",
        json=[{"display_name": "GPX4"}],
        status=200,
    )

    responses.add(
        responses.GET,
        "https://grch37.rest.ensembl.org/map/human/GRCh37/19:1105813..1105814/GRCh38?content-type=application/json",
        json=[],
        status=200,
    )

    responses.add(
        responses.GET,
        "https://grch37.rest.ensembl.org/map/human/GRCh37/19:1106232..1106238/GRCh38?content-type=application/json",
        json=[],
        status=200,
    )

    # Setup authorized client + node
    ok_token = _setup(mock_app, test_client, test_node, database)

    query_patient = {"patient": gpx4_patients[0]}
    for feat in query_patient["patient"]["genomicFeatures"]:
        assert feat["gene"]["id"] == "GPX4"

    assert len(gpx4_patients) == 2
    inserted_ids = []
    for pat in gpx4_patients:
        mme_pat = mme_patient(pat, True)
        inserted_ids.append(backend_add_patient(database, mme_pat))
    assert len(inserted_ids) == 2

    assert database["matches"].find_one() is None

    response = mock_app.test_client().post(
        MATCH_ENDPOINT,
        data=json.dumps(query_patient),
        headers=auth_headers(ok_token),
    )
    assert response.status_code == 200

    data = json.loads(response.data)
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 2
    assert "patient" in data["results"][0]
    assert "score" in data["results"][0]
    assert "contact" in data["results"][0]["patient"]

    match = database["matches"].find_one()
    for res in match["results"]:
        for pat in res["patients"]:
            assert pat["patient"]["contact"]
            assert pat["score"]["patient"] > 0

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
    response = mock_app.test_client().post("".join([MATCH_EXTERNAL_ENDPOINT, inserted_id]))
    # server should return 401 (not authorized)
    assert response.status_code == 401

    # send an authorized request with a patient ID that doesn't exist on server:
    response = mock_app.test_client().post(
        "".join([MATCH_EXTERNAL_ENDPOINT, "not_a_valid_ID"]), headers=auth_headers(ok_token)
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
        "".join([MATCH_EXTERNAL_ENDPOINT, inserted_id]), headers=auth_headers(ok_token)
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["message"] == "Could not find any other node connected to this MatchMaker server"

    # Try to send a request for a match on a node that does not exist
    response = mock_app.test_client().post(
        "".join([MATCH_EXTERNAL_ENDPOINT, inserted_id, "?node=meh"]), headers=auth_headers(ok_token)
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    # And check that node not found is in response message
    assert data["message"] == "ERROR. Could not find any connected node with id meh in database"

    # insert a connected node
    add_node(mongo_db=mock_app.db, obj=test_node, is_client=False)  # required for external matches
    # send a request to match patients against all nodes
    response = mock_app.test_client().post(
        "".join([MATCH_EXTERNAL_ENDPOINT, inserted_id]), headers=auth_headers(ok_token)
    )

    # Response should be valid
    assert response.status_code == 200
    # And a new match should be created in matches collection
    assert database["matches"].find_one()

    # send a request to match patients against the specific existing node:
    response = mock_app.test_client().post(
        "".join([MATCH_EXTERNAL_ENDPOINT, inserted_id, "?node=", test_node["_id"]]),
        headers=auth_headers(ok_token),
    )
    # Response should be valid
    assert response.status_code == 200

    # And a new match should be created in matches collection. So total matches are 2
    results = database["matches"].find()
    assert len(list(results)) == 2


def unauth_headers():
    head = {
        "Content-Type": CONTENT_TYPE,
        "Accept": [CONTENT_TYPE, "application/json"],
        "X-Auth-Token": "wrong_token",
    }
    return head


def auth_headers(test_token):
    head = {
        "Content-Type": CONTENT_TYPE,
        "Accept": [CONTENT_TYPE, "application/json"],
        "X-Auth-Token": test_token,
    }
    return head
