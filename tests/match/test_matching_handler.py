# -*- coding: utf-8 -*-
import requests
from patientMatcher.utils.add import load_demo, backend_add_patient
from patientMatcher.parse.patient import mme_patient
from patientMatcher.match.handler import internal_matcher, save_async_response, external_matcher

def test_internal_matching(demo_data_path, database, json_patients):
    """Testing the combined matching algorithm"""

    # load demo data to mock database using function located under utils/load
    inserted_ids = load_demo(demo_data_path, database)
    assert len(inserted_ids) == 50 # 50 test cases are loaded

    # format test patient for query:
    test_mme_patients = [ mme_patient(patient) for patient in json_patients ]

    a_patient = test_mme_patients[0]
    assert a_patient

    match_obj = internal_matcher(database, a_patient, 0.5, 0.5)
    matches = match_obj['results'][0]['patients']
    assert len(matches) == 5 # default number of MAX_RESULTS

    higest_scored_patient = matches[0]
    lowest_scored_patient = matches[-1]

    assert higest_scored_patient['score']['patient'] > lowest_scored_patient['score']['patient']


def test_internal_matching_with_threshold(demo_data_path, database, json_patients):
    # load demo data to mock database using function located under utils/load
    inserted_ids = load_demo(demo_data_path, database)
    assert len(inserted_ids) == 50 # 50 test cases are loaded

    # format test patient for query:
    test_mme_patients = [ mme_patient(patient) for patient in json_patients ]

    a_patient = test_mme_patients[0]
    assert a_patient

    match_obj = internal_matcher( database=database, patient_obj=a_patient, max_pheno_score=0.5, max_geno_score=0.5,
        max_results=5, score_threshold=0.1)
    matches = match_obj['results'][0]['patients']
    assert len(matches) == 1


def test_external_matching(database, test_node, json_patients, monkeypatch):
    """Testing the function that trigger patient matching across connected nodes"""

    patient = json_patients[0]

    # insert test node object in database
    database['nodes'].insert_one(test_node)

    # insert patient object in database
    inserted_ids = backend_add_patient(mongo_db=database, patient=patient, match_external=False)
    assert inserted_ids

    class MockResponse(object):
        def __init__(self):
            self.status_code = 200
        def json(self):
            resp = {
                "disclaimer" : "This is a test disclaimer",
                "results" : json_patients
            }
            return resp

    def mock_response(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr( requests , 'request', mock_response )

    ext_m_result = external_matcher(database, patient, test_node['_id'])
    assert isinstance(ext_m_result, dict)
    assert ext_m_result['data']['patient']['id'] == patient['id']
    assert ext_m_result['has_matches'] == True
    assert ext_m_result['match_type'] == 'external'


def test_save_async_response(database, test_node):
    """Testing the function that saves an async response object to database"""

    # Test database should not contain async responses
    assert database['async_responses'].find().count() == 0

    # Save an async response using the matching handler
    save_async_response(database=database, node_obj=test_node,
        query_id='test', query_patient_id='test_patient')

    # async_responses database collection should now contain one object
    async_response = database['async_responses'].find_one()
    assert async_response['query_id'] == 'test'
    assert async_response['query_patient_id'] == 'test_patient'
    assert async_response['node']['id'] == test_node['_id']
    assert async_response['node']['label'] == test_node['label']
