# -*- coding: utf-8 -*-

import json
from jsonschema import validate, RefResolver, FormatChecker
from patientMatcher.utils.gene import symbol_to_ensembl, entrez_to_symbol, ensembl_to_symbol
from pkgutil import get_data
import logging

LOG = logging.getLogger(__name__)
SCHEMA_FILE = "api.json"


def mme_patient(json_patient, convert_to_ensembl=False):
    """
    Accepts a json patient and converts it to a MME patient,
    formatted as required by patientMatcher database

    Args:
        patient_obj(dict): a patient object as in https://github.com/ga4gh/mme-apis
        convert_to_entrez(bool): convert gene IDs to ensembl IDs

    Returns:
        mme_patient(dict) : a mme patient entity
    """

    # Make sure gene objects are defined by ensembl IDs
    if json_patient.get("genomicFeatures") and convert_to_ensembl:
        format_genes(json_patient)

    mme_patient = {
        "_id": json_patient["id"],
        "id": json_patient["id"],
        "label": json_patient.get("label"),
        "sex": json_patient.get("sex"),
        "contact": json_patient["contact"],
        "features": json_patient.get("features"),
        "genomicFeatures": json_patient.get("genomicFeatures"),
        "disorders": json_patient.get("disorders"),
        "species": json_patient.get("species"),
        "ageOfOnset": json_patient.get("ageOfOnset"),
        "inheritanceMode": json_patient.get("inheritanceMode"),
    }

    # remove keys with empty values from mme_patient object
    mme_patient = {k: v for k, v in mme_patient.items() if v is not None}

    return mme_patient


def json_patient(mme_patient):
    """Converts a mme patient into a json-like as in the MME APIs

    Args:
        mme_patient(dict): a patient object as it is stored in database

    Returns:
        json_patient(dict): a patient object conforming to MME API
    """
    json_patient = mme_patient
    if "id" not in mme_patient:
        json_patient["id"] = json_patient["_id"]
    if "_id" in json_patient:
        json_patient.pop("_id")

    return json_patient


def features_to_hpo(features):
    """Extracts HPO terms from a list of phenotype features of a patient

    Args:
        features(list): a list of features dictionaries

    Returns:
        hpo_terms(list): a list of HPO terms. Example : ['HP:0100026', 'HP:0009882', 'HP:0001285']
    """
    if features is None:
        return []
    hpo_terms = [feature.get("_id") for feature in features if feature.get("_id")]
    if len(hpo_terms) == 0:
        hpo_terms = [feature.get("id") for feature in features if feature.get("id")]
    return hpo_terms


def disorders_to_omim(disorders):
    """Extracts OMIM terms from a list of disorders of a patient

    Args:
        disorders(list): a list of disorders

    Returns:
        omim_terms(list): a list of OMIM terms. Example : ['MIM:616007', 'MIM:614665']
    """
    if disorders is None:
        return []
    omim_terms = [disorder.get("id") for disorder in disorders if disorder.get("id")]
    return omim_terms


def format_genes(patient_obj):
    """Checks if patient's gFeatures gene ids are defined as ensembl ids.
    If they are entrez ids or symbols thet will be converted to ensembl IDs.

    Args:
        patient_obj(dict): A patient object with genotype features
    """
    formatted_features = []
    for feature in patient_obj.get("genomicFeatures", []):
        if "gene" in feature and feature["gene"].get("id"):
            gene = feature["gene"]["id"]
            gene_id, symbol = _convert_gene(gene)
            if symbol:
                feature["gene"]["_geneName"] = symbol  # add non-standard but informative field
            feature["gene"]["id"] = gene_id
        formatted_features.append(feature)

    if formatted_features:
        patient_obj["genomicFeatures"] = formatted_features


def _convert_gene(gene):
    """Convert provided gene id to Ensembl gene id return it with eventual HGNC gene symbol

    Args:
        gene(str): can be either be:
            - a string representing an entrez id. example: "4556"
            - a HGNC gene symbol, example: "GPX4"
            - An Ensembl gene ID, example: "ENSG00000167468"

    Returns:
        gene(str): An Ensembl gene ID, example: "ENSG00000167468"
        symbol(str): HGNC gene symbol, example: "GPX4"
    """
    symbol = None
    try:
        if gene.startswith("ENSG"):  # Ensembl gene ID
            symbol = ensembl_to_symbol(gene)
            return gene, symbol
        if gene.isdigit():  # Entrez id
            symbol = entrez_to_symbol(gene)
        else:  # HGNC gene symbol
            symbol = gene
        if symbol:
            gene = symbol_to_ensembl(symbol) or gene

    except Exception as ex:
        LOG.error(
            f"An error occurred while converting gene format using the Ensembl Rest API: {ex}"
        )

    return gene, symbol


def gtfeatures_to_genes_symbols(gtfeatures):
    """Extracts all gene names from a list of genomic features
    Args:
        gtfeatures(list): a list of genomic features objects

    Returns:
        gene_set(list): a list of unique gene names contained in the features
    """
    genes = []
    symbols = []
    for feature in gtfeatures:
        if "gene" in feature:
            gene = feature["gene"].get("id")
            gene, symbol = _convert_gene(gene)
            if gene:
                genes.append(gene)
            if symbol:
                symbols.append(symbol)

    gene_set = list(set(genes))
    symbol_set = list(set(symbols))
    return gene_set, symbol_set


def gtfeatures_to_variants(gtfeatures):
    """Extracts all variants from a list of genomic features

    Args:
        gtfeatures(list): a list of genomic features objects

    Returns:
        variants(list): a list of variants
    """
    variants = []
    for feature in gtfeatures:
        if "variant" in feature:
            variants.append(feature["variant"])

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
    schema = "#/definitions/response"
    if is_request:
        schema = "#/definitions/request"

    LOG.info("Validating against SCHEMA {}".format(schema))

    # get API definitions
    schema_data = json.loads(get_data("patientMatcher.resources", SCHEMA_FILE).decode("utf-8"))
    resolver = RefResolver.from_schema(schema_data)
    format_checker = FormatChecker()
    resolver_schema = resolver.resolve_from_url(schema)
    validate(json_obj, resolver_schema, resolver=resolver, format_checker=format_checker)
