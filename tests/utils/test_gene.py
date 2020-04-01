# -*- coding: utf-8 -*-

from patientMatcher.utils.gene import (
    entrez_to_symbol,
    ensembl_to_symbol,
    symbol_to_ensembl,
)


def test_ensembl_to_symbol():
    # Test converting ensembl ID to official gene symbol

    ensembl_id = "ENSG00000103591"
    symbol = ensembl_to_symbol(ensembl_id)
    assert symbol == "AAGAB"


def test_symbol_to_ensembl():
    # Test converting official gene symbol to ensembl ID

    symbol = "AAGAB"
    ensembl_id = symbol_to_ensembl(symbol)
    assert ensembl_id == "ENSG00000103591"


def test_entrez_to_symbol():
    # Test converting entrez ID to gene symbol
    entrez_id = "3735"
    symbol = entrez_to_symbol(entrez_id)
    assert symbol == "KARS"
