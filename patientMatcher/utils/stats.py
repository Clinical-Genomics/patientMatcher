# -*- coding: utf-8 -*-
import logging
from datetime import date

LOG = logging.getLogger(__name__)

def general_metrics(db):
    """Create an object with database metrics

    Args:
        db(pymongo.database.Database)

    Returns:
        metrics(dict): According to the MME API it should be a dictionary like this:
            {
                "metrics": {
                    "numberOfCases": 0,
                    "numberOfSubmitters": 0,
                    "numberOfGenes": 0,
                    "numberOfUniqueGenes": 0,
                    "numberOfVariants": 0,
                    "numberOfUniqueVariants": 0,
                    "numberOfFeatures": 0,
                    "numberOfUniqueFeatures": 0,
                    "numberOfFeatureSets": 0, # endpoint is not returning this, at the moment
                    "numberOfUniqueGenesMatched": 0,
                    "numberOfCasesWithDiagnosis": 0,
                    "numberOfRequestsReceived": 0,
                    "numberOfPotentialMatchesSent": 0,
                    "dateGenerated": "2017-08-24",

                },
                "disclaimer": "Disclaimer text...",
                "terms": "Terms text..."
            }
    """
    # get gene/occurrence for all genes in db
    n_genes = 0
    gene_occurrs = item_occurrence(db, 'genomicFeatures', 'genomicFeatures.gene', 'genomicFeatures.gene.id')
    for gene_count in gene_occurrs:
        n_genes += gene_count['count']

    # get numberOfUniqueVariants/occurrence for all variants in db
    variant_occurr = item_occurrence(db, 'genomicFeatures', 'genomicFeatures.variant', 'genomicFeatures.variant')
    n_vars = 0
    for var in variant_occurr:
        n_vars += var.get('count')

    # get feature/occurrence for all features in db
    n_feat = 0
    feat_occurr = item_occurrence(db, 'features', 'features.id')
    for feat in feat_occurr:
        n_feat += feat.get('count')

    # include in unique_gene_matches only matches actively returned by the server (internal)
    match_type = {'match_type':'internal'}
    unique_gene_matches = db.matches.distinct('results.patients.patient.genomicFeatures.gene', match_type)

    metrics = {
        'numberOfCases' : db.patients.find().count(),
        'numberOfSubmitters' : len(db.patients.distinct('contact.href')),
        'numberOfGenes' : n_genes,
        'numberOfUniqueGenes': len(db.patients.distinct('genomicFeatures.gene')),
        'numberOfVariants' : n_vars,
        'numberOfUniqueVariants' : len(db.patients.distinct('genomicFeatures.variant')),
        'numberOfFeatures' : n_feat,
        'numberOfUniqueFeatures' : len(db.patients.distinct('features.id')),
        'numberOfUniqueGenesMatched' : len(unique_gene_matches),
        'numberOfCasesWithDiagnosis' : db.patients.find({'disorders': {'$exists': True, '$ne' : []} }).count(),
        'numberOfRequestsReceived' : db.matches.find({'match_type':'internal'}).count(),
        'numberOfPotentialMatchesSent' : db.matches.find({'match_type':'internal', 'has_matches': True}).count(),
        'dateGenerated' : str(date.today())
    }
    return metrics


def item_occurrence(db, unw1, group, unw2=None):
    """Get a list of item/occurrence in patient collection

    Args:
        db(pymongo.database.Database)
        unw1(string): first nested unwind item
        group(string): item to group results by
        unw2(string): second nested unwind item # none if nested level is missing

    Returns:
        item_occurr(list) example: [{'id':'item_obj', 'count': item_occurrence}, ..]
    """
    # create query pipeline
    pipeline = [{"$unwind": ''.join(['$',unw1])}]
    if unw2:
        pipeline.append({"$unwind": ''.join(['$',unw2])})
    pipeline.append({"$group": {"_id": ''.join(['$',group]), "count": {"$sum": 1}}})
    item_occurr = list(db.patients.aggregate(pipeline))
    return item_occurr
