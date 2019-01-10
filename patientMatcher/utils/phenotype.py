# -*- coding: utf-8 -*-

import logging
import requests
import json

from patientMatcher.parse.monarch import parse_monarch_matches

LOG = logging.getLogger(__name__)
MONARCH_BASE = 'https://monarchinitiative.org/analyze/phenotypes.json?input_items='

def monarch_phenotypes(hpo_terms):
    """Builds a phenotype profile by sending a request with HPO terms
       to the Monarch Phenotype Profile Analysis.
       json file returned in the response is parsed to obtain the phenotypes with
       highes matching scores (combined score from submitted HPO terms)

       Direct query example: https://monarchinitiative.org/analyze/phenotypes?input_items=HP%3A0100026+HP%3A0009882+HP%3A0001285&mode=search&target_species=9606&limit=100&gene_list=

       Args:
        hpo_terms(list): a list of HPO terms such as: ['HP:0100026', 'HP:0009882', '(HP:0001285']

       Returns:
        computed_phenotypes(list): a list of objects such as :
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
    url = ''.join([MONARCH_BASE, '+'.join(hpo_terms), '&limit=20', '&target_species=9606' ])
    LOG.info(url)
    response = None
    computed_phenotypes = []
    try:
        LOG.info('Sending HPO terms to Monarch service..')
        response = requests.get(url, timeout=10)
        json_resp = response.json()
        LOG.info('server returned {} phenotypes.'.format(len(json_resp['results'])))

    except Exception as err:
        LOG.info('An error occurred while sending HTTP request to server ({})'.format(err))

    if type(json_resp) == dict: # received computed phenotypes from Monarch, parse them
        computed_phenotypes = parse_monarch_matches(json_resp)

    return computed_phenotypes
