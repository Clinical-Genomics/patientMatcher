# -*- coding: utf-8 -*-
import requests
from patientMatcher.match.handler import external_matcher, internal_matcher, save_async_response
from patientMatcher.parse.patient import mme_patient
from patientMatcher.utils.add import backend_add_patient


def test_internal_matching(database, gpx4_patients):
    """Testing the combined matching algorithm"""

    # load 2 test patients in mock database
    for patient in gpx4_patients:
        mme_pat = mme_patient(patient, True)  # convert gene symbol to ensembl
        database["patients"].insert_one(mme_pat).inserted_id

    # 2 patients should be inserted
    results = database["patients"].find({"genomicFeatures.gene.id": "ENSG00000167468"})
    assert len(list(results)) == 2

    # test matching of one of the 2 patients against both patients in database
    proband_patient = mme_patient(gpx4_patients[0], True)

    match = internal_matcher(database, proband_patient, 0.5, 0.5)
    match_patients = match["results"][0]["patients"]
    assert len(match_patients) == 2

    higest_scored_patient = match_patients[0]  # first returned patient has higher score
    lowest_scored_patient = match_patients[-1]  # last returned patient has lower score

    assert higest_scored_patient["score"]["patient"] > lowest_scored_patient["score"]["patient"]


def test_internal_matching_with_threshold(database, gpx4_patients):
    # load 2 test patients in mock database
    for patient in gpx4_patients:
        mme_pat = mme_patient(patient, True)  # convert gene symbol to ensembl
        database["patients"].insert_one(mme_pat).inserted_id

    # 2 patients should be inserted
    results = database["patients"].find({"genomicFeatures.gene.id": "ENSG00000167468"})
    assert len(list(results)) == 2

    # test matching of one of the 2 patients against both patients in database
    proband_patient = mme_patient(gpx4_patients[0], True)

    match = internal_matcher(
        database=database,
        patient_obj=proband_patient,
        max_pheno_score=0.5,
        max_geno_score=0.5,
        max_results=5,
        score_threshold=0.5,
    )
    match_patients = match["results"][0]["patients"]
    assert len(match_patients) == 1  # one patient is filtered out by search threshold


def test_external_matching(database, test_node, gpx4_patients, monkeypatch):
    """Testing the function that trigger patient matching across connected nodes"""

    patient = gpx4_patients[0]

    # insert test node object in database
    database["nodes"].insert_one(test_node)

    # insert patient object in database
    inserted_ids = backend_add_patient(mongo_db=database, patient=patient, match_external=False)
    assert inserted_ids

    class MockResponse(object):
        def __init__(self):
            self.status_code = 200

        def json(self):
            resp = {"disclaimer": "This is a test disclaimer", "results": gpx4_patients}
            return resp

    def mock_response(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(requests, "request", mock_response)

    ext_m_result = external_matcher(database, patient, test_node["_id"])
    assert isinstance(ext_m_result, dict)
    assert ext_m_result["data"]["patient"]["id"] == patient["id"]
    assert ext_m_result["has_matches"] == True
    assert ext_m_result["match_type"] == "external"


def test_save_async_response(database, test_node):
    """Testing the function that saves an async response object to database"""

    # Test database should not contain async responses
    results = database["async_responses"].find()
    assert len(list(results)) == 0

    # Save an async response using the matching handler
    save_async_response(
        database=database, node_obj=test_node, query_id="test", query_patient_id="test_patient"
    )

    # async_responses database collection should now contain one object
    async_response = database["async_responses"].find_one()
    assert async_response["query_id"] == "test"
    assert async_response["query_patient_id"] == "test_patient"
    assert async_response["node"]["id"] == test_node["_id"]
    assert async_response["node"]["label"] == test_node["label"]
