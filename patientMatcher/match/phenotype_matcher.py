#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from patientMatcher.parse.patient import features_to_hpo, disorders_to_omim

LOG = logging.getLogger(__name__)

def match(database, max_score, features, disorders):
    """Handles phenotype matching algorithm

    Args:
        database(pymongo.database.Database)
        max_score(float): a number between 0 and 1
        features(list): a list of phenotype feature objects (example ID = HP:0008619)
        disorders(list): a list of OMIM diagnoses (example ID = MIM:616007 )

    Returns:
        matches(dict): a dictionary of patient matches with phenotype matching score
    """
    matches = {}

    hpo_terms = []
    omim_terms = []
    query_fields = []

    LOG.info('\n\n###### Running phenotype matcher module ######')

    if features: # at least one HPO term is specified
        hpo_terms = features_to_hpo(features)
        query_fields.append({'features.id': {"$in" : hpo_terms}})

    if disorders: # at least one OMIM term was provided
        omim_terms = disorders_to_omim(disorders)
        query_fields.append({'disorders.id': {"$in" : omim_terms}})

    # build a database query taking into account patient features (HPO terms) and disorders (omim)
    if len(query_fields) > 0:

        query = { '$or' : query_fields }

        LOG.info(query)
        pheno_matching_patients = list(database['patients'].find(query))

        LOG.info("\n\nFOUND {} patients matching patients's phenotype tracts\n\n".format(len(pheno_matching_patients)))

        for patient in pheno_matching_patients:
            similarity = evaluate_pheno_similariy(hpo_terms, omim_terms, patient, max_score)

            match = {
                'patient_obj' : patient,
                'pheno_score' : similarity,
            }
            matches[patient['_id']] = match

    return matches


def evaluate_pheno_similariy(hpo_terms, disorders, pheno_matching_patient, max_similarity):
    """Evaluates the similarity of two patients based on phenotype features

        Args:
            hpo_terms(list): HPO terms of the query patient
            disorders(list): OMIM disorders of the query patient
            pheno_matching_patient(patient_obj): a patient object from the database
            max_similarity(float): a floating point number representing the highest value allowed for a feature

        Returns:
            patient_similarity(float): the computed genetic similarity among the patients
    """
    return 1
