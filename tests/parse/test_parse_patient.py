#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from patientMatcher.parse.patient import features_to_hpo, disorders_to_omim, gtfeatures_to_genes

def test_features_to_hpo_no_features():
    # Make sure the function returns [] if patient doesn't have HPO terms
    result = features_to_hpo(None)
    assert result == []

def test_disorders_to_omim_no_omim():
    # Make sure the function returns [] if patient doesn't have OMIM terms
    result = disorders_to_omim(None)
    assert result == []

def test_gtfeatures_to_genes():
    # Test parsing of genotype feature
    required_symbols = ['AAGAB','LIMS2']

    g_features = [
        {'gene':{'id':'ENSG00000103591'}},
        {'gene':{'id':'ENSG00000072163'}}
    ]
    # Make sure that Ensembl rest API convert ensembl IDs to gene symbols
    gene_set = gtfeatures_to_genes(g_features)
    for item in gene_set:
        assert item in required_symbols
