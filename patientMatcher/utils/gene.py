#!/usr/bin/env python
# -*- coding: utf-8 -*-
import patientMatcher.utils.ensembl_rest_client as ensembl_client


def entrez_to_symbol(entrez_id):
    """Convert entrez id to gene symbol

    Accepts:
        entrez_id(str) ex. "3735"

    Returns
        gene_symbol(str) ex. BRAF
    """
    client = ensembl_client.EnsemblRestApiClient()
    url = "".join([client.server, "/xrefs/name/human/", entrez_id, "?external_db=EntrezGene"])
    results = client.send_request(url)
    for gene in results:  # result is an array. First element is enough
        return gene["display_id"]


def symbol_to_ensembl(gene_symbol):
    """Convert gene symbol to ensembl id

    Accepts:
        gene_symbol(str) ex. LIMS2

    Returns:
        ensembl_id(str) ex. ENSG00000072163
    """
    client = ensembl_client.EnsemblRestApiClient()
    url = "".join([client.server, "/xrefs/symbol/homo_sapiens/", gene_symbol, "?external_db=HGNC"])
    results = client.send_request(url)
    for gene in results:  # result is an array. First element is enough
        if gene["id"].startswith("ENSG"):  # it's the ensembl id
            return gene["id"]


def ensembl_to_symbol(ensembl_id):
    """Converts ensembl id to gene symbol

    Accepts:
        ensembl_id(str): an ensembl gene id. Ex: ENSG00000103591

    Returns:
        gene_symbol(str): an official gene symbol. Ex: AAGAB
    """

    client = ensembl_client.EnsemblRestApiClient()
    url = "".join([client.server, "/lookup/id/", ensembl_id])
    results = client.send_request(url)
    return results.get("display_name", None)
