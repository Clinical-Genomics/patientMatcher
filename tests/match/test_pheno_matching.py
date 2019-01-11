# -*- coding: utf-8 -*-

import pytest

from patientMatcher.utils.phenotype import monarch_phenotypes
from patientMatcher.utils.load import load_demo
from patientMatcher.match.phenotype_matcher import match as pheno_match
from patientMatcher.parse.patient import mme_patient


def test_monarch_phenotypes():
    """Test that the Monarch Phenotype Profile Analysis is up and running
       and the query of HPO terms returns the expected result
    """
    HPO_terms = ['HP:0100026', 'HP:0009882', 'HP:0001285']

    computed_phenotypes = monarch_phenotypes(HPO_terms)

    # only the 5 topmost hits should be returned
    assert len(computed_phenotypes) == 5

    # matches should be ranked from the highest
    assert computed_phenotypes[0]['combined_score'] > computed_phenotypes[4]['combined_score']


def test_phenotype_matching(json_patients, database, demo_data_path):
    """test the algorithm that compares the phenotype of a query patient against the database"""

    # insert demo patients into test database
    inserted_ids = load_demo(demo_data_path, database)
    assert len(inserted_ids) == 50 # 50 test cases should be loaded

    query_patient = json_patients[0]
    assert query_patient

    formatted_patient =  mme_patient(query_patient)
    matches = pheno_match(database, 0.25, formatted_patient['features'],  formatted_patient['disorders'])

    assert len(matches) > 0

    for patient in matches:
        assert patient['_id']
        assert patient['pheno_score'] > 0
