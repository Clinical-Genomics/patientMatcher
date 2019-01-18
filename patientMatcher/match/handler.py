#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from patientMatcher.match.genotype_matcher import match as genomatch
from patientMatcher.match.phenotype_matcher import match as phenomatch
from patientMatcher.parse.patient import json_patients

LOG = logging.getLogger(__name__)

def database_matcher(database, patient_obj, max_pheno_score, max_geno_score):
    """Handles a query patient matching against the database of patients

    Args:
        database(pymongo.database.Database)
        patient_obj(dic): a mme formatted patient object
        max_pheno_score(float): a number between 0 and 1
        max_geno_score(float): a number between 0 and 1

    Returns:
        sorted_json_matches(list): a list of json-like patient matches sorted by descending score
    """
    pheno_matches = []
    geno_matches = []
    matches = []

    # phenotype score can be obtained if patient has an associated phenotype (HPO or OMIM terms)
    if len(patient_obj['features']) or len(patient_obj['disorders']) > 0:
        LOG.info('Matching phenotypes against database patients..')
        pheno_matches = phenomatch(database, max_pheno_score, patient_obj['features'], patient_obj['disorders'])

    # genomic score can be obtained if patient has at least one genomic feature
    if len(patient_obj['genomicFeatures']) > 0:
        LOG.info('Matching variants/genes against database patients..')
        geno_matches = genomatch(database, patient_obj['genomicFeatures'], max_geno_score)

    # obtain unique list of all patient IDs returned by the 2 algorithms:
    pheno_m_keys = list(pheno_matches.keys())
    geno_m_keys = list(geno_matches.keys())
    unique_patients = list(set(pheno_m_keys + geno_m_keys))

    # create matching result objects with combined score from the 2 algorithms
    for key in unique_patients:
        pheno_score = 0
        geno_score = 0
        patient_obj = None

        if key in pheno_m_keys:
            pheno_score = pheno_matches[key]['pheno_score']
            patient_obj = pheno_matches[key]['patient_obj']

        if key in geno_m_keys:
            geno_score = geno_matches[key]['geno_score']
            patient_obj = geno_matches[key]['patient_obj']

        p_score = pheno_score + geno_score
        #patient_obj.pop('monarch_phenotypes')
        patient_obj['score'] = {
            'patient' : p_score,
            'genotype' : geno_score,
            'phenotype' : pheno_score
        }
        matches.append(patient_obj)

    # sort patient matches by patient (combined) score
    sorted_matches = sorted(matches, key=lambda k : k['score']['patient'], reverse=True)
    sorted_json_matches = json_patients(sorted_matches)

    # return sorted matches
    return sorted_json_matches
