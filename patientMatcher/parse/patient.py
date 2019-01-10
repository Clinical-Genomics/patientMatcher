# -*- coding: utf-8 -*-

import logging
from patientMatcher.utils.phenotype import monarch_phenotypes

LOG = logging.getLogger(__name__)

def mme_patient(json_patient, compute_phenotypes=False):
    """
        Accepts a json patient and converts it to a MME patient,
        formatted as required by patientMatcher database

        Args:
            patient_obj(dict): a patient object as in https://github.com/ga4gh/mme-apis
            compute_phenotypes(bool) : if True most likely phenotypes will be computed using Monarch

        Returns:
            mme_patient(dict) : a mme patient entity
    """

    # fix patient's features:
    for feature in json_patient.get('features'):
        feature['_id'] = feature.get('id')
        feature.pop('id')

    mme_patient = {
        '_id' : json_patient['id'],
        'label' : json_patient.get('label'),
        'contact' : json_patient['contact'],
        'features' : json_patient['features'],
        'genomicFeatures' : json_patient.get('genomicFeatures'),
        'disorders' : json_patient.get('disorders'),
        'species' : json_patient.get('species'),
        'ageOfOnset' : json_patient.get('ageOfOnset'),
        'inheritanceMode' : json_patient.get('inheritanceMode')
    }

    if compute_phenotypes: # build Monarch phenotypes from patients' HPO terms
        hpo_terms = features_to_hpo(json_patient['features'])
        computed_phenotypes = monarch_phenotypes(hpo_terms)
        mme_patient['monarch_phenotypes'] = computed_phenotypes

    return mme_patient


def features_to_hpo(features):
    """Extracts HPO terms from a list of phenotype features of a patient

        Args:
            features(list): a list of features dictionaries

        Returns:
            hpo_terms(list): a list of HPO terms. Example : ['HP:0100026', 'HP:0009882', 'HP:0001285']
    """

    hpo_terms = [feature['_id'] for feature in features]
    return hpo_terms
