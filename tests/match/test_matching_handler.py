# -*- coding: utf-8 -*-
import requests
import responses
from patientMatcher.match.handler import external_matcher, internal_matcher
from patientMatcher.parse.patient import mme_patient
from patientMatcher.utils.add import backend_add_patient


@responses.activate
def test_internal_matching(mock_app, database, gpx4_patients):
    """Testing the combined matching algorithm"""

    # GIVEN a mocked Ensembl REST API:
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


@responses.activate
def test_internal_matching_with_threshold(mock_app, database, gpx4_patients):

    # GIVEN a mocked Ensembl REST API:
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
