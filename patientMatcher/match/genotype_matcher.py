#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
LOG = logging.getLogger(__name__)

def match(database, gt_features, max_score):
    """Handles genotype matching algorithm

    Args:
        database(pymongo.database.Database)
        gt_features(list): a list of genomic features (objects)
        max_score(float): a number between 0 and 1

    Returns:
        matches(list): a list of patient matches with GT score
    """
    matches = []
    n_gtfeatures = len(gt_features)

    if n_gtfeatures > 0:

        max_feature_similarity = max_score/n_gtfeatures

        LOG.info('Query patient has {0} genotype features. .'.format(n_gtfeatures))
        LOG.info('Each GT feature will contribute with a weight of {0} to a total GT score (max GT score is {1})'.format( max_feature_similarity, max_score ))

        # Look for database patients having variants in the same genes:
        genes = get_query_genes(gt_features)

        if genes:
            LOG.info('unique genes:{}'.format(get_query_genes(gt_features)))

            query = {
                "genomicFeatures.gene.id" : {"$in" : genes}
            }
            # query patients collection by gene name
            gene_matching_patients = list(database['patients'].find(query)) # a list of patients with genomic feature/s in one or more of the query genes
            LOG.info("Found {0} patients matching genes:{1}".format(len(gene_matching_patients), genes))

            # assign a genetic similarity score for each of these patients
            for patient in gene_matching_patients:
                gt_similarity = evaluate_GT_similarity(gt_features, patient['genomicFeatures'], max_feature_similarity)
                match = {
                    '_id' : patient['_id'],
                    'label' : patient.get('label'),
                    'patient_obj' : patient,
                    'gt_score' : gt_similarity,
                    'type' : 'canonical' # patients share variants in same genes
                }
                matches.append(match)

        # Look also for variant matches outside genes:
        non_canonical_vars = non_canonical_variants(gt_features)
        query = {
            "genomicFeatures.variant" : {"$in" : non_canonical_vars}
        }
        outside_genes_matching_patients = list(database['patients'].find(query))
        LOG.info("Found {0} patients with matches outside genes:".format(len(outside_genes_matching_patients)))

        for patient in outside_genes_matching_patients:
            gt_similarity = evaluate_GT_similarity(gt_features, patient['genomicFeatures'], max_feature_similarity)
            match = {
                '_id' : patient['_id'],
                'label' : patient.get('label'),
                'patient_obj' : patient,
                'gt_score' : gt_similarity,
                'type' : 'non_canonical' # patient with matching variants outside genes
            }
            matches.append(match)
            LOG.info(match)
    else:
        LOG.info('Query patient has no genomic features. GT score is 0.')

    return matches


def get_query_genes(gtfeatures):
    """Extracts all gene names from a list of genomic features

    Args:
        gtfeatures(list): a list of genomic features objects

    Returns:
        gene_set(list): a list of unique gene names contained in the features
    """
    genes = []
    for feature in gtfeatures:
        if 'gene' in feature and feature['gene']['id']: # collect non-null gene IDs
            genes.append(feature['gene']['id'])
    gene_set = list(set(genes))
    return gene_set


def non_canonical_variants(gtfeatures):
    """Extracts all variants that fall ouside genes from a list of genomic features

    Args:
        gtfeatures(list): a list of genomic features objects

    Returns:
        nc_variants(list): a list of non-canonical variants (variants outside genes)
    """
    nc_variants = []
    for feature in gtfeatures:
        if 'variant' in feature:
            if not 'gene' in feature or feature['gene']['id'] == "":
                nc_variants.append(feature['variant'])

    return nc_variants


def evaluate_GT_similarity(query_features, db_patient_features, max_feature_similarity):
    """
        Args:
            query_patient(list of dictionaries): genomic features of the query patient
            db_patient_features(list of dictionaries): genomic features of a patient in patientMatcher database
            max_similarity(float): a floating point number representing the highest value allowed for a feature

                ## Explanation: for a query patient with one feature max_similarity will be equal to MAX_GT_SCORE
                   For a patient with 2 features max_similarity will be MAX_GT_SCORE/2 and so on.

        Returns:
            patient_similarity(float): the computed genetic similarity among the patients
    """
    # gene_matching similarity among features = 0.25 of the max_feature_similarity
    # exact variant matching among features = max_feature_similarity

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
    LOG.info('Evaluated similarity among patients. Sum of GT features:{}'.format(features_sum))
    return features_sum
