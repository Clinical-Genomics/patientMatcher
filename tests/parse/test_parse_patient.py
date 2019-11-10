#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from patientMatcher.parse.patient import format_genes

from patientMatcher.parse.patient import features_to_hpo, disorders_to_omim, gtfeatures_to_genes

def test_features_to_hpo_no_features():
    # Make sure the function returns [] if patient doesn't have HPO terms
    result = features_to_hpo(None)
    assert result == []

def test_disorders_to_omim_no_omim():
    # Make sure the function returns [] if patient doesn't have OMIM terms
    result = disorders_to_omim(None)
    assert result == []
