# -*- coding: utf-8 -*-

from patientMatcher.utils.add import load_demo
from patientMatcher.match.phenotype_matcher import match as pheno_match
from patientMatcher.parse.patient import mme_patient

def test_phenotype_matching(json_patients, database, demo_data_path):
    """test the algorithm that compares the phenotype of a query patient against the database"""

    # insert demo patients into test database
    inserted_ids = load_demo(demo_data_path, database, 'patientMatcher.host.se')
    assert len(inserted_ids) == 50 # 50 test cases should be loaded

    query_patient = json_patients[0]
    assert query_patient

    # this patient has HPO terms and OMIM diagnosis
    formatted_patient =  mme_patient(query_patient)
    assert len(formatted_patient['features']) > 0
    assert len(formatted_patient['disorders']) > 0

    matches_HPO_OMIM = pheno_match(database, 0.5, formatted_patient['features'],  formatted_patient['disorders'])
    assert len(matches_HPO_OMIM.keys()) > 0
    for key,value in matches_HPO_OMIM.items():
        assert 'patient_obj' in value
        assert value['pheno_score'] > 0

    features = formatted_patient['features']
    disorders = formatted_patient['disorders']
    # remove HPO terms from the query patient, test that the algorithm works anyway
    # because matching will use OMIM disorders
    formatted_patient['features'] = []
    matches_OMIM = pheno_match(database, 0.5, formatted_patient['features'],  formatted_patient['disorders'])
    assert len(matches_OMIM.keys()) > 0
    for key,value in matches_OMIM.items():
        assert 'patient_obj' in value
        assert value['pheno_score'] > 0

    # remove the OMIM diagnosis from patient object. The algorithm should work
    # but it shouldn't return any match
    formatted_patient['disorders'] = []
    matches_no_phenotypes = pheno_match(database, 0.5, formatted_patient['features'],  formatted_patient['disorders'])
    assert len(matches_no_phenotypes.keys()) == 0

    # Add again features. The algorithm works again because HPO terms will be used
    formatted_patient['features'] = features
    matches_HPO = pheno_match(database, 0.5, formatted_patient['features'],  formatted_patient['disorders'])
    assert len(matches_HPO.keys()) > 0
    for key,value in matches_HPO.items():
        assert 'patient_obj' in value
        assert value['pheno_score'] > 0

    # make sure that matches obtained when OMIM and HPO terms are present are more or equal than
    # when either of these phenotype terms is present by itself
    assert len(matches_HPO_OMIM.keys()) >= len(matches_OMIM.keys())
    assert len(matches_HPO_OMIM.keys()) >= len(matches_HPO.keys())
