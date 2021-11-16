#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from patientMatcher.parse.patient import (
    disorders_to_omim,
    features_to_hpo,
    gtfeatures_to_variants,
    href_validate,
    mme_patient,
)


def test_href_validate_wrong_url():
    """Test href_validate function with a malformed URL"""
    assert href_validate("google") is False


def test_href_validate_valid_url():
    """Test href_validate function with a valid URL"""
    assert href_validate("http://google.com") is True


def test_href_validate_wrong_email():
    """Test href_validate function with a mailto link and wrong email syntax"""
    assert href_validate("me@patientmatcher.se") is False


def test_href_validate_valid_email():
    """Test href_validate function with a mailto link and valid email"""
    assert href_validate("mailto:me@patientmatcher.se") is True


def test_features_to_hpo_no_features():
    """Make sure the function returns [] if patient doesn't have associated HPO terms"""
    result = features_to_hpo(None)
    assert result == []


def test_disorders_to_omim_no_omim():
    """Make sure the function returns [] if patient doesn't have associated OMIM terms"""
    result = disorders_to_omim(None)
    assert result == []


def test_mme_patient_gene_symbol(gpx4_patients, database):
    """Test format a patient with HGNC gene symbol"""

    test_patient = gpx4_patients[0]
    gene_name = test_patient["genomicFeatures"][0]["gene"]["id"]  # "GPX4"
    # Before conversion patient's gene id is a gene symbol
    assert gene_name.startswith("ENSG") is False
    mme_formatted_patient = mme_patient(test_patient, True)  # Convert gene symbol to Ensembl
    # After conversion formatted patient's gene id should be an Ensembl id
    assert mme_formatted_patient["genomicFeatures"][0]["gene"]["id"].startswith("ENSG")
    assert mme_formatted_patient["genomicFeatures"][0]["gene"]["_geneName"] == gene_name


def test_mme_patient_entrez_gene(entrez_gene_patient, database):
    """Test format a patient with entrez gene"""
    # Before conversion patient's gene id is an entrez gene ID
    assert entrez_gene_patient["genomicFeatures"][0]["gene"]["id"] == "3735"
    mme_formatted_patient = mme_patient(entrez_gene_patient, True)  # convert genes to Ensembl
    # After conversion formatted patient's gene id should be an Ensembl id
    assert mme_formatted_patient["genomicFeatures"][0]["gene"]["id"].startswith("ENSG")
    assert mme_formatted_patient["genomicFeatures"][0]["gene"]["_geneName"]  # it's "KARS"


def test_gtfeatures_to_variants(patient_37):
    """Test the function that parses variants dictionaries from patient's genomic features"""
    # GIVEN a patient containing 1 genomic feature (and one variant)
    gt_features = patient_37["patient"]["genomicFeatures"]
    assert len(gt_features) == 1

    # WHEN gtfeatures_to_variants is used to extract variants from gt_features
    variants = gtfeatures_to_variants(gt_features)

    # THEN it should return 2 variants
    assert len(variants) == 2

    # One with genome build GRCh37
    assert variants[0]["assembly"] == "GRCh37"
    # And one with genome build GRCh38
    assert variants[1]["assembly"] == "GRCh38"
