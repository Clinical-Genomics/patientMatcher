#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from patientMatcher.parse.patient import features_to_hpo, disorders_to_omim, monarch_hit_ids
from patientMatcher.utils.phenotype import monarch_phenotypes

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
    monarch_terms = []
    query_fields = []

    LOG.info('\n\n###### Running phenotype matcher module ######')

    if features: # at least one HPO term is specified
        hpo_terms = features_to_hpo(features)
        query_fields.append({'features.id': {"$in" : hpo_terms}})

    if disorders: # at least one OMIM term was provided
        omim_terms = disorders_to_omim(disorders)
        query_fields.append({'disorders.id': {"$in" : omim_terms}})

    if features: # compute most likely phenotypes
        monarch_phtypes = monarch_phenotypes(hpo_terms)
        monarch_terms = monarch_hit_ids(monarch_phtypes)
        query_fields.append({'monarch_phenotypes.hit_id': {"$in" : monarch_terms}})

    # build a database query taking into account patient features (HPO terms), disorders (omim) and eventual monarch phenotypes
    if len(query_fields) > 0:

        query = { '$or' : query_fields }

        LOG.info(query)
        pheno_matching_patients = list(database['patients'].find(query))

        LOG.info("\n\nFOUND {} patients matching patients's phenotype tracts\n\n".format(len(pheno_matching_patients)))

        for patient in pheno_matching_patients:
            similarity = evaluate_pheno_similariy(hpo_terms, omim_terms, monarch_terms, patient, max_score)

            match = {
                'patient_obj' : patient,
                'pheno_score' : similarity,
            }
            matches[patient['_id']] = match

    return matches


def evaluate_pheno_similariy(hpo_terms, disorders, monarch_phtypes, pheno_matching_patient, max_similarity):
    """Evaluates the similarity of two patients based on phenotype features

        Args:
            hpo_terms(list): HPO terms of the query patient
            disorders(list): OMIM disorders of the query patient
            monarch_phtypes(list): ID of the Monarch-computed disorders of the query patient
            pheno_matching_patient(patient_obj): a patient object from the database
            max_similarity(float): a floating point number representing the highest value allowed for a feature

        Returns:
            patient_similarity(float): the computed genetic similarity among the patients
    """
    patient_similarity = 0

    hpo_score = 0
    omim_score = 0
    monarch_score = 0

    # Compute similarity of HPO terms:
    max_hpo_score = max_similarity/2 # half of the phenotype score will depend on HPO terms matching
    db_patient_hpo_terms = features_to_hpo(pheno_matching_patient['features']) # HPO terms of the matching patient
    hpo_score = evaluate_subcategories(hpo_terms, db_patient_hpo_terms, max_hpo_score)

    max_omim_score = 0
    max_monarch_score = 0
    if len(disorders) == 0: # no OMIM diagnoses available
        max_monarch_score = max_similarity/2 # half of the phenotype score will depend on computed phenotypes from Monarch
    else:
        max_omim_score = max_similarity/4 # 25% of the phenotype score will depend on OMIM terms matching
        max_monarch_score = max_similarity/4 # 25% of the phenotype score will depend on computed phenotypes from Monarch

        # Compute similarity of OMIM terms:
        db_patient_omim_terms = disorders_to_omim(pheno_matching_patient['disorders'])
        omim_score = evaluate_subcategories(disorders, db_patient_omim_terms, max_omim_score)

    # Compute similarity of Monarch-computed diagnoses:
    db_patient_monarch_terms = monarch_hit_ids(pheno_matching_patient.get('monarch_phenotypes',[]))
    monarch_score = evaluate_subcategories(monarch_phtypes, db_patient_monarch_terms, max_monarch_score)

    patient_similarity = hpo_score + omim_score + monarch_score
    return patient_similarity


def evaluate_subcategories(list1, list2, max_score):
    """returns a numerical representation of the similarity of two lists of strings

        Args:
            list1(list): a list of strings (this is a list of items from the query patient)
            list2(list): another list of strings (list of items from the patients in database)
            max_score(float): the maximum value to return if the lists are identical

        Returns:
            matching_score(float): a number reflecting the similarity between the lists
    """
    matching_score = 0
    if len(list1)>0:
        list_item_score = max_score/len(list1) # the max value of each matching item between lists
        n_shared_items = len(set(list1).intersection(list2)) # number of elements shared between the lists
        matching_score = n_shared_items * list_item_score
    return matching_score
