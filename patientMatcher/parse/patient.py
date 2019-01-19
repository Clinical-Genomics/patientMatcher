# -*- coding: utf-8 -*-

import json
from jsonschema import validate, RefResolver, FormatChecker
from pkgutil import get_data
import logging
from patientMatcher.utils.phenotype import monarch_phenotypes

LOG = logging.getLogger(__name__)
SCHEMA_FILE = 'api.json'

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

    # remove keys with empty values from mme_patient object
    mme_patient = {k:v for k,v in mme_patient.items() if v is not None}

    return mme_patient


def json_patient(mme_patient):
    """ Converts a mme patient into a json-like as in the MME APIs

        Args:
            mme_patient(dict): a patient object as it is stored in database

        Returns:
            json_patient(dict): a patient object conforming to MME API
    """
    json_patient = mme_patient
    if 'monarch_phenotypes' in json_patient:
        json_patient.pop('monarch_phenotypes')
    json_patient['id'] = json_patient['_id']
    json_patient.pop('_id')

    return json_patient


def features_to_hpo(features):
    """Extracts HPO terms from a list of phenotype features of a patient

        Args:
            features(list): a list of features dictionaries

        Returns:
            hpo_terms(list): a list of HPO terms. Example : ['HP:0100026', 'HP:0009882', 'HP:0001285']
    """

    hpo_terms = [feature.get('_id') for feature in features if feature.get('_id')]
    if len(hpo_terms) == 0:
        hpo_terms = [feature.get('id') for feature in features if feature.get('id')]
    return hpo_terms


def disorders_to_omim(disorders):
    """Extracts OMIM terms from a list of disorders of a patient

        Args:
            disorders(list): a list of disorders

        Returns:
            omim_terms(list): a list of OMIM terms. Example : ['MIM:616007', 'MIM:614665']
    """

    omim_terms = [disorder.get('id') for disorder in disorders if disorder.get('id')]
    return omim_terms


def monarch_hit_ids(monarch_phenotypes):
    """Extracts monarch hit ids from a list of monarch phenotype objects

        Args:
            monarch_phenotypes(list) example:[{'combined_score': 79, 'hit_label': 'Rienhoff syndrome', 'hit_id': 'MONDO:0014262'}, ..]

        Returns:
            monarch_terms(list) example: [ 'MONDO:0014262' ..]
    """

    monarch_terms = [pheno.get('hit_id') for pheno in monarch_phenotypes if pheno.get('hit_id')]
    return monarch_terms


def gtfeatures_to_genes(gtfeatures):
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


def gtfeatures_to_variants(gtfeatures):
    """Extracts all variants from a list of genomic features

    Args:
        gtfeatures(list): a list of genomic features objects

    Returns:
        variants(list): a list of variants
    """
    variants = []
    for feature in gtfeatures:
        if 'variant' in feature:
            variants.append(feature['variant'])

    return variants


def validate_api(json_obj, is_request):
    """Validates a request against the MME API
       The code for the validation against the API and the API specification is taken from
       this project: https://github.com/MatchmakerExchange/reference-server

    Args:
        json_obj(dict): json request or response to validate
        is_request(bool): True if it is a request, False if it is a response

    Returns
        validated(bool): True or False
    """
    validated = True
    schema = '#/definitions/response'
    if is_request:
        schema = '#/definitions/request'

    LOG.info("Validating against SCHEMA {}".format(schema))

    # get API definitions
    schema_data = json.loads(get_data('patientMatcher.resources', SCHEMA_FILE).decode('utf-8'))
    resolver = RefResolver.from_schema(schema_data)
    format_checker = FormatChecker()
    resolver_schema = resolver.resolve_from_url(schema)
    validate(json_obj, resolver_schema, resolver=resolver, format_checker=format_checker)
