#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from patientMatcher.parse.patient import features_to_hpo, disorders_to_omim, mme_patient

def test_features_to_hpo_no_features():
    # Make sure the function returns [] if patient doesn't have HPO terms
    result = features_to_hpo(None)
    assert result == []

def test_disorders_to_omim_no_omim():
    # Make sure the function returns [] if patient doesn't have OMIM terms
    result = disorders_to_omim(None)
    assert result == []

def test_mme_patient_gene_symbol(gpx4_patients,database):
    # Test format a patient with gene symbol

    test_patient = gpx4_patients[0]
    # Before conversion patient's gene id is a gene symbol
    assert test_patient['genomicFeatures'][0]['gene']['id'].startswith('ENSG') is False
    mme_formatted_patient = mme_patient(test_patient, True) # Convert gene symbol to Ensembl
    # After conversion formatted patient's gene id should be an Ensembl id
    assert mme_formatted_patient['genomicFeatures'][0]['gene']['id'].startswith('ENSG')


def test_mme_patient_entrez_gene(entrez_gene_patient, database):
    #Test format a patient with entrez gene

    # Before conversion patient's gene id is an entrez gene ID
    assert entrez_gene_patient['genomicFeatures'][0]['gene']['id'] == "3735"
    mme_formatted_patient = mme_patient(entrez_gene_patient, True) # convert genes to Ensembl
    # After conversion formatted patient's gene id should be an Ensembl id
    assert mme_formatted_patient['genomicFeatures'][0]['gene']['id'].startswith('ENSG')
