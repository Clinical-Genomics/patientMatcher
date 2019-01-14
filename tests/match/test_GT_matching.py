# -*- coding: utf-8 -*-

from patientMatcher.utils.add import load_demo
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
    matches = match(database, gt_features, 0.5)
    assert len(matches.keys()) == 4 # 4 matching patients are returned

    for key, value in matches.items():
        # patient object should also be returned
        assert 'patient_obj' in value

        # genotype score for each patient should be higher than 0
        assert value['geno_score'] > 0

    # make sure that the algorithm works even if a gene or a variant object is missing:
    # remove gene ID from first gt feature
    gt_features[0]['gene']['id'] = ''
    matches = match(database, gt_features, 0.5)
    # same patients should be returned, because of variant matching instead
    assert len(matches) == 4

    # Remove variant object from second gt feature
    gt_features[1]['variant'] = None
    matches = match(database, gt_features, 0.5)
    # same patients shpuld be returned, because of gene matching instead
    assert len(matches.keys()) == 4
