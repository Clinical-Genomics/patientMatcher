# -*- coding: utf-8 -*-

import pytest

from patientMatcher.utils.phenotype import monarch_phenotypes

def test_monarch_phenotypes():
    """Test that the Monarch Phenotype Profile Analysis is up and running
       and the query of HPO terms returns the expected result
    """
    HPO_terms = ['HP:0100026', 'HP:0009882', 'HP:0001285']

    computed_phenotypes = monarch_phenotypes(HPO_terms)

    # only the 10 topmost hits should be returned
    assert len(computed_phenotypes) == 10

    # matches should be ranked from the highest
    assert computed_phenotypes[0]['combined_score'] > computed_phenotypes[9]['combined_score']
