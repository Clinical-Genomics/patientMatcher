# -*- coding: utf-8 -*-

from patientMatcher.utils.add import load_demo, backend_add_patient
from patientMatcher.parse.patient import mme_patient
from patientMatcher.match.handler import internal_matcher, save_async_response, external_matcher

def test_internal_matching(demo_data_path, database, json_patients):
    """Testing the combined matching algorithm"""

    # load demo data to mock database using function located under utils/load
    inserted_ids = load_demo(demo_data_path, database, False)
    assert len(inserted_ids) == 50 # 50 test cases are loaded

    # format test patient for query:
    test_mme_patients = [ mme_patient(patient) for patient in json_patients ]

    a_patient = test_mme_patients[0]
    assert a_patient

    match_obj = internal_matcher(database, a_patient, 0.5, 0.5)
    matches = match_obj['results'][0]['patients']
    assert len(matches) > 0

    higest_scored_patient = matches[0]
    lowest_scored_patient = matches[-1]

    assert higest_scored_patient['score']['patient'] > lowest_scored_patient['score']['patient']


def test_external_matching(database, test_node, json_patients):
    """Testing the function that trigger patient matching across connected nodes"""

    patient = json_patients[0]

    # insert test node object in database
    database['nodes'].insert_one(test_node)

    # insert patient object in database
    inserted_ids = backend_add_patient(mongo_db=database, host='patientMatcher.host.se', patient=patient, match_external=False)
    assert inserted_ids

    ext_m_result = external_matcher(database, 'pmatcher', patient, test_node['_id'])
    assert isinstance(ext_m_result, dict)
    assert ext_m_result['data']['patient']['id'] == patient['id']
    assert ext_m_result['has_matches'] == False
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
