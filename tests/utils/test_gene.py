# -*- coding: utf-8 -*-
import responses
from patientMatcher.utils.ensembl_rest_client import requests
from patientMatcher.utils.gene import ensembl_to_symbol, entrez_to_symbol, symbol_to_ensembl


@responses.activate
def test_entrez_to_symbol():
    """Test the function converting entrez ID to gene symbol"""
    # GIVEN an entrez ID
    entrez_id = "3735"
    # THAT should return a symbol
    symbol = "KARS"

    # GIVEN a mocked Ensembl REST API converting entrez ID to gene symbol
    responses.add(
        responses.GET,
        f"https://grch37.rest.ensembl.org/xrefs/name/human/{entrez_id}?external_db=EntrezGene",
        json=[{"display_id": symbol}],
        status=200,
    )

    # The EnsemblRestApiClient should return the right Ensembl ID
    assert entrez_to_symbol(entrez_id) == symbol


@responses.activate
def test_symbol_to_ensembl_one_ensembl_id():
    """
    Test function converting official gene symbol to ensembl ID using the Ensembl REST API
    Test case when the Ensembl API return only one Ensembl ID as result
    """

    # GIVEN a gene symbol
    hgnc_symbol = "AAGAB"
    # That should return an Ensembl ID
    ensembl_id = "ENSG00000103591"

    # GIVEN a mocked Ensembl REST API converting gene symbol to Ensembl ID
    responses.add(
        responses.GET,
        f"https://grch37.rest.ensembl.org/xrefs/symbol/homo_sapiens/{hgnc_symbol}?external_db=HGNC",
        json=[{"id": "ENSG00000103591", "type": "gene"}],
        status=200,
    )

    # The EnsemblRestApiClient should return the right Ensembl ID
    assert ensembl_id == symbol_to_ensembl(hgnc_symbol)


def test_symbol_to_ensembl_multiple_ensembl_id(monkeypatch):
    """Test function converting official gene symbol to ensembl ID using the Ensembl REST API
    Test case when the Ensembl API return multiple Ensembl gene IDs for one HGNC gene symbol
    """
    # GIVEN a gene symbol
    hgnc_symbol = "SKI"
    # Corresponfing to 2 different ensembl IDs
    rigth_ensembl_id = "ENSG00000157933"
    wrong_ensembl_id = "ENSG00000054392"

    # GIVEN a patched API response that returns data for 2 ensembl genes
    class MockResponse(object):
        def __init__(self, url):
            self.status_code = 200
            self.url = url

        def json(self):
            if hgnc_symbol in self.url:  # initial query, returns 2 Ensembl IDs
                return [
                    {"id": rigth_ensembl_id, "type": "gene"},
                    {"id": wrong_ensembl_id, "type": "gene"},
                ]
            elif (
                rigth_ensembl_id in self.url
            ):  # second call to the API, returns the HGNC info for the right gene
                return [
                    {
                        "primary_id": "HGNC:10896",
                        "display_id": "SKI",
                        "description": "SKI proto-oncogene",
                        "dbname": "HGNC",
                    }
                ]
            elif (
                wrong_ensembl_id in self.url
            ):  # second call to the API, returns the HGNC info for the wrong gene
                return [
                    {
                        "primary_id": "HGNC:18270",
                        "display_id": "HHAT",
                        "description": "hedgehog acyltransferase",
                        "dbname": "HGNC",
                    }
                ]

    def mock_get(url, headers):
        return MockResponse(url)

    monkeypatch.setattr(requests, "get", mock_get)

    # The EnsemblRestApiClient should return the right Ensembl ID
    ensembl_id = symbol_to_ensembl(hgnc_symbol)
    assert ensembl_id == rigth_ensembl_id


@responses.activate
def test_ensembl_to_symbol(monkeypatch):
    """Test converting ensembl ID to official gene symbol using the Ensembl APIs"""

    # GIVEN an Ensembl ID
    ensembl_id = "ENSG00000103591"
    # THAT should return a certain symbl
    symbol = "AAGAB"

    # GIVEN a patched API response
    class MockResponse(object):
        def __init__(self):
            self.status_code = 200

        def json(self):
            return {"display_name": symbol}

    def mock_get(url, headers):
        return MockResponse()

    monkeypatch.setattr(requests, "get", mock_get)

    # The EnsemblRestApiClient should return the right symbl
    assert ensembl_to_symbol(ensembl_id) == symbol
