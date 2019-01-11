# -*- coding: utf-8 -*-

import logging
import json

LOG = logging.getLogger(__name__)

def parse_monarch_matches(json_response):
    """Extracts top matches from a json response from a Monarch Phenotype
       Profile Analysis

        Args:
            json_response(dict) : a json file coming from https://monarchinitiative.org/analyze/phenotypes

        Returns:
            monarch_matches(list): a list containing the top phenotype matches
                Example:
                    [
                        {
                            'combinedScore' : 79,
                            'hit_label' : 'multiple exostoses with spastic Tetraparesis',
                            'hit_id' : 'MONDO:0008020',
                        },
                        {
                            'combinedScore' : 72,
                            'hit_label' : 'brachydactyly type A1D',
                            'hit_id' : 'MONDO:0019676',
                        },
                        ...
                    ]
    """
    monarch_matches = []

    # extract 10 topmost results
    results = json_response['results'][:5]

    for result in results:
        match = {
            'combined_score' : result['combinedScore'],
            'hit_label' : result['j']['label'],
            'hit_id': result['j']['id']
        }
        monarch_matches.append(match)

    if len(monarch_matches)>0:
        LOG.info('Monarch hits parsed successfully.')
    return monarch_matches
