# -*- coding: utf-8 -*-

from patientMatcher.utils.add import load_demo
from patientMatcher.parse.patient import mme_patient
from patientMatcher.match.handler import internal_matcher as dbmatcher

def test_internal_matching(demo_data_path, database, json_patients):
    """Testing the combined matching algorithm"""

    # load demo data to mock database using function located under utils/load
    inserted_ids = load_demo(demo_data_path, database, False)
    assert len(inserted_ids) == 50 # 50 test cases are loaded

    # format test patient for query:
    test_mme_patients = [ mme_patient(patient) for patient in json_patients ]

    a_patient = test_mme_patients[0]
    assert a_patient

    match_obj = dbmatcher(database, a_patient, 0.5, 0.5)
    matches = match_obj['results']
    assert len(matches) > 0

    higest_scored_patient = matches[0]
    lowest_scored_patient = matches[-1]

    assert higest_scored_patient['score']['patient'] > lowest_scored_patient['score']['patient']
