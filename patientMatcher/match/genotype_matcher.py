#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from patientMatcher.parse.patient import gtfeatures_to_genes, gtfeatures_to_variants
LOG = logging.getLogger(__name__)

def match(database, gt_features, max_score):
    """Handles genotype matching algorithm

    Args:
        database(pymongo.database.Database)
        gt_features(list): a list of genomic features (objects)
        max_score(float): a number between 0 and 1

    Returns:
        matches(dict): a dictionary of patient matches with GT score
    """
    matches = {}
    n_gtfeatures = len(gt_features)

    LOG.info('\n\n###### Running genome matcher module ######')

    if n_gtfeatures > 0:

        max_feature_similarity = max_score/n_gtfeatures

        LOG.info('Query patient has {0} genotype features.'.format(n_gtfeatures))
        LOG.info('Each GT feature will contribute with a weight of {0} to a total GT score (max GT score is {1})'.format( max_feature_similarity, max_score ))

        query = {}
        query_fields = []

        genes = gtfeatures_to_genes(gt_features)
        if genes:
            query_fields.append({'genomicFeatures.gene.id' : {"$in" : genes}})

        variants = gtfeatures_to_variants(gt_features)
        if variants:
            query_fields.append({'genomicFeatures.variant': {"$in" : variants} })

        if len(query_fields) > 0:
        # prepare a query that takes into account genes and variants in general (also outside genes!)
            query = { '$or' : query_fields }
            LOG.info('Querying database for genomic features:{}'.format(query))

            # query patients collection
            matching_patients = list(database['patients'].find(query)) # a list of patients with genomic feature/s in one or more of the query genes
            LOG.info("Found {0} matching patients".format(len(matching_patients)))

            # assign a genetic similarity score to each of these patients
            for patient in matching_patients:
                gt_similarity = evaluate_GT_similarity(gt_features, patient['genomicFeatures'], max_feature_similarity)
                match = {
                    'patient_obj' : patient,
                    'geno_score' : gt_similarity,
                }
                matches[patient['_id']] = match

    LOG.info("\n\nFOUND {} patients matching patients's genomic tracts\n\n".format(len(matching_patients)))
    return matches


def evaluate_GT_similarity(query_features, db_patient_features, max_feature_similarity):
    """ Evaluates the genomic similarity of two patients based on genomic similarities

        Args:
            query_patient(list of dictionaries): genomic features of the query patient
            db_patient_features(list of dictionaries): genomic features of a patient in patientMatcher database
            max_similarity(float): a floating point number representing the highest value allowed for a feature

                ## Explanation: for a query patient with one feature max_similarity will be equal to MAX_GT_SCORE
                   For a patient with 2 features max_similarity will be MAX_GT_SCORE/2 and so on.

        Returns:
            patient_similarity(float): the computed genetic similarity among the patients
    """

    matched_features = []
    n_feature = 0

    # loop over the query patient's features
    for feature in query_features:

        matched_features.append(0)
        q_gene = feature['gene'] # query feature's gene id
        q_variant = feature.get('variant', None) # query feature's variant. Not mandatory.

        #loop over the database patient's features:
        for matching_feature in db_patient_features:
            m_gene = matching_feature['gene'] # matching feature's gene id
            m_variant = matching_feature.get('variant') # matching feature's variant. Not mandatory.

            if q_variant and m_variant: # compare only if they have a value. They don't have to be in genes!
                if q_variant == m_variant:
                    matched_features[n_feature] = max_feature_similarity

            elif q_gene and m_gene and matched_features[n_feature] == 0: # Genes not null and no previous variant matching
                if q_gene == m_gene: # matching genes, at least
                    matched_features[n_feature] =  max_feature_similarity/4 #(0.25 of the max_feature_similarity)

        n_feature += 1

    features_sum = sum(matched_features)
    return features_sum
