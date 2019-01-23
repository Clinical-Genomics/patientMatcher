#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import datetime
import requests
import json
from werkzeug.datastructures import Headers
from patientMatcher.match.genotype_matcher import match as genomatch
from patientMatcher.match.phenotype_matcher import match as phenomatch
from patientMatcher.parse.patient import json_patient

LOG = logging.getLogger(__name__)

def internal_matcher(database, patient_obj, max_pheno_score, max_geno_score):
    """Handles a query patient matching against the database of patients

    Args:
        database(pymongo.database.Database)
        patient_obj(dic): a mme formatted patient object
        max_pheno_score(float): a number between 0 and 1
        max_geno_score(float): a number between 0 and 1

    Returns:
        sorted_matches(list): a list of patient matches sorted by descending score
    """
    json_pat = json_patient(patient_obj)
    pheno_matches = []
    geno_matches = []
    matches = []

    # phenotype score can be obtained if patient has an associated phenotype (HPO or OMIM terms)
    if len(patient_obj['features']) or len(patient_obj['disorders']) > 0:
        LOG.info('Matching phenotypes against database patients..')
        pheno_matches = phenomatch(database, max_pheno_score, patient_obj.get('features',[]), patient_obj.get('disorders',[]))

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
        score = {
            'patient' : p_score,
            'genotype' : geno_score,
            'phenotype' : pheno_score
        }
        match = {
            'patient' : json_patient(patient_obj),
            'score' : score
        }
        matches.append(match)

    # sort patient matches by patient (combined) score
    sorted_matches = sorted(matches, key=lambda k : k['score']['patient'], reverse=True)

    # this is saved to server, regardless of the results returned by the nodes
    has_matches = False
    if sorted_matches:
        has_matches = True

    internal_match = {
        'created' : datetime.datetime.now(),
        'has_matches' : has_matches,
        'data' : {'patient' : json_pat}, # description of the patient submitted
        'results' : sorted_matches,
        'match_type' : 'internal'
    }
    database['matches'].insert_one(internal_match)

    # return sorted matches
    return sorted_matches


def external_matcher(database, patient):
    """Handles a query patient matching against all connected MME nodes

    Args:
        database(pymongo.database.Database)
        patient(dict) : a MME patient entity

    Returns:
        matching_id(str): The ID of the matching object created in database
    """

    connected_nodes = list(database['nodes'].find()) #get all connected nodes
    if len(connected_nodes) == 0:
        LOG.error("Could't find any connected MME nodes. Aborting external matching.")
        return None

    # create request headers
    headers = Headers()
    data = {'patient': json_patient(patient)} # convert into something that follows the API specs

    # this is saved to server, regardless of the results returned by the nodes
    external_match = {
        'created' : datetime.datetime.now(),
        'has_matches' : False, # it changes if a similar patient is returned by any other MME nodes
        'data' : data, # description of the patient submitted
        'results' : [],
        'errors' : [],
        'match_type' : 'external'
    }

    LOG.info("Matching patient against {} nodes..".format(len(connected_nodes)))
    for node in connected_nodes:

        server_name = node['_id']
        node_url = node['matching_url']
        token = node['auth_token']
        request_content_type = node['accepted_content']

        headers = {'Content-Type': request_content_type, 'Accept': 'application/vnd.ga4gh.matchmaker.v1.0+json', "X-Auth-Token": token}
        LOG.info('sending HTTP request to server: "{}"'.format(server_name))
        # send request and get response from server
        json_response = None
        server_return = None
        try:
            server_return = requests.request(
                method = 'POST',
                url = node_url,
                headers = headers,
                data = json.dumps(data)
            )
            json_response = server_return.json()
        except Exception as json_exp:
            error = json_exp
            LOG.error('Server returned error:{}'.format(error))
            external_match['errors'].append(str(type(error)))

        if json_response:
            LOG.info('server returns the following response: {}'.format(json_response))
            results = json_response['results']
            if len(results):
                external_match['has_matches'] = True
                external_match['results'].append(results)

    # save external match in database, "matches" collection
    matching_id = database['matches'].insert_one(external_match).inserted_id

    # INSERT HERE THE CODE TO SEND ALL EVENTUAL MATCHES BY EMAIL TO CLIENT!!!

    return matching_id
