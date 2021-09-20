# -*- coding: utf-8 -*-
import responses
from patientMatcher.utils.gene import ensembl_to_symbol, entrez_to_symbol, symbol_to_ensembl


def test_ensembl_to_symbol():
    # Test converting ensembl ID to official gene symbol

    ensembl_id = "ENSG00000103591"
    symbol = ensembl_to_symbol(ensembl_id)
    assert symbol == "AAGAB"


@responses.activate
def test_symbol_to_ensembl(mock_symbol_2_ensembl):
    """Test function converting official gene symbol to ensembl ID using the Ensembl REST API"""

    hgnc_symbol = "AAGAB"

    # GIVEN a mocked Ensembl REST API
    responses.add(
        responses.GET,
        f"https://grch37.rest.ensembl.org/xrefs/symbol/homo_sapiens/{hgnc_symbol}?external_db=HGNC",
        json=[{"id": "ENSG00000103591"}],
        status=200,
    )

    ensembl_id = symbol_to_ensembl(hgnc_symbol)
    assert ensembl_id == "ENSG00000103591"


def test_entrez_to_symbol():
    # Test converting entrez ID to gene symbol
    entrez_id = "3735"
    symbol = entrez_to_symbol(entrez_id)
    assert symbol == "KARS"
