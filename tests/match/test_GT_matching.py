# -*- coding: utf-8 -*-

import pytest
from patientMatcher.utils.load import load_demo
from patientMatcher.parse.patient import mme_patient
from patientMatcher.match.genotype_matcher import match

def test_genotype_matching(demo_data_path, database, json_patients):
    """Testing the genotyping matching algorithm"""

    # load demo data in mock database
    # load demo data to mock database using function located under utils/load
    inserted_ids = load_demo(demo_data_path, database, False)
    assert len(inserted_ids) == 50 # 50 test cases are loaded

    # test conversion to format required for the database:
    test_mme_patients = [ mme_patient(patient) for patient in json_patients]

    # make sure 2 json patient are correctly parsed
    assert len(test_mme_patients) == 2

    # test matching of a patient (with variants in genes) against the demo patients in database
    a_patient = test_mme_patients[0]
    assert a_patient

    # assert patient has genomic features
    gt_features = a_patient['genomicFeatures']
    assert len(gt_features) == 3 # should have 3 features to match

    # match features against database of demo patients:
    matches = match(database, gt_features, 0.75)
    assert len(matches) == 4 # 4 matching patients are returned

    for patient in matches:
        # make sure matching patient's ID is returned
        assert '_id' in patient

        # patient object should also be returned
        assert 'patient_obj' in patient

        # genotype score for each patient should be higher than 0
        assert patient['gt_score'] > 0


    # test matching of a patient (with variant outside genes) against the demo patients in database
    nonconforming_patient = test_mme_patients[1]

    # assert that genomicFeature has an empty gene field
    assert nonconforming_patient['genomicFeatures'][0]['gene']['id'] == ''

    gt_features = nonconforming_patient['genomicFeatures']

    # match features against database of demo patients:
    matches = match(database, gt_features, 0.75)
    assert len(matches) == 2

    for patient in matches:
        patient['type'] == 'non_canonical'
        patient['gt_score'] == 0.75 # variant exact match
