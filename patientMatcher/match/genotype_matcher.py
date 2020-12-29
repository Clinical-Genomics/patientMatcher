#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from patientMatcher.parse.patient import (
    gtfeatures_to_genes_symbols,
    gtfeatures_to_variants,
    lift_variant,
)

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

    LOG.info("\n\n###### Running genome matcher module ######")

    if n_gtfeatures > 0:
        max_feature_similarity = max_score / n_gtfeatures

        LOG.info("Query patient has {0} genotype features.".format(n_gtfeatures))
        LOG.info(
            "Each GT feature will contribute with a weight of {0} to a total GT score (max GT score is {1})".format(
                max_feature_similarity, max_score
            )
        )

        query = {}
        query_fields = []

        genes, symbols = gtfeatures_to_genes_symbols(gt_features)
        if genes:
            query_fields.append({"genomicFeatures.gene.id": {"$in": genes}})
        if symbols:
            query_fields.append({"genomicFeatures.gene._geneName": {"$in": symbols}})

        # Obtain variants and the corresponding variants in the other genome build from the genotype features
        variants = gtfeatures_to_variants(gt_features)
        if variants:
            query_fields.append({"genomicFeatures.variant": {"$in": variants}})

        if len(query_fields) > 0:
            # prepare a query that takes into account genes and variants in general (also outside genes!)
            query = {"$or": query_fields}
            LOG.info("Querying database for genomic features:{}".format(query))

            # query patients collection
            matching_patients = list(
                database["patients"].find(query)
            )  # a list of patients with genomic feature/s in one or more of the query genes
            LOG.info("Found {0} matching patients".format(len(matching_patients)))

            # assign a genetic similarity score to each of these patients
            for patient in matching_patients:
                gt_similarity = evaluate_GT_similarity(
                    gt_features, patient["genomicFeatures"], max_feature_similarity
                )
                LOG.info("GT similarity score is {}".format(gt_similarity))
                match = {
                    "patient_obj": patient,
                    "geno_score": gt_similarity,
                }
                matches[patient["_id"]] = match

    LOG.info(
        "\n\nFOUND {} patients matching patients's genomic tracts\n\n".format(
            len(matching_patients)
        )
    )
    return matches


def evaluate_GT_similarity(query_features, db_patient_features, max_feature_similarity):
    """Evaluates the genomic similarity of two patients based on genomic similarities

    Args:
        query_patient(list of dictionaries): genomic features of the query patient
        db_patient_features(list of dictionaries): genomic features of a patient in patientMatcher database
        max_feature_similarity(float): a floating point number representing the highest value allowed for a single feature

            ## Explanation: for a query patient with one feature max_similarity will be equal to MAX_GT_SCORE
               For a patient with 2 features max_similarity will be MAX_GT_SCORE/2 and so on.

    Returns:
        patient_similarity(float): the computed genetic similarity among the patients
    """

    matched_features = []
    n_feature = 0

    # loop over the query patient's features
    for feature in query_features:
        matched_features.append(0)  # score for matching of every feature is initially 0
        q_gene_id = feature["gene"]["id"]  # query feature's gene id
        q_gene_symbol = feature["gene"].get("_geneName")  # query feature's gene symbol

        # Do liftover for query variant in order to maximize perfect matching chances
        q_variant = feature.get("variant")  # query feature's variant. Not mandatory.
        lifted_q_variant = lift_variant(q_variant) if q_variant else []

        # loop over the database patient's features:
        for matching_feature in db_patient_features:
            m_gene_id = matching_feature["gene"]["id"]  # matching feature's gene id
            m_gene_symbol = matching_feature["gene"].get(
                "_geneName"
            )  # matching feature's gene symbol
            m_variant = matching_feature.get(
                "variant"
            )  # matching feature's variant. Not mandatory.

            # if variants are matching or lifted query variant matches with matched patients variant
            # ->assign max matching score
            if q_variant == m_variant or m_variant in lifted_q_variant:
                matched_features[n_feature] = max_feature_similarity

            elif q_gene_id == m_gene_id:  # matching genes
                matched_features[n_feature] = (
                    max_feature_similarity / 4
                )  # (0.25 of the max_feature_similarity)
            elif q_gene_symbol and q_gene_symbol == m_gene_symbol:
                matched_features[n_feature] = (
                    max_feature_similarity / 4
                )  # (0.25 of the max_feature_similarity)
        n_feature += 1

    features_sum = sum(matched_features)
    return features_sum
