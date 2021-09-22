# -*- coding: UTF-8 -*-
import pytest
from patientMatcher.utils import ensembl_rest_client as ensembl_api
from requests.exceptions import MissingSchema


def test_except_on_invalid_response():
    """Test function that creates exception with message when response returned from Ensembl REST API has status code !=200"""

    # GIVEN a response from Ensembl service with status != 200
    client = ensembl_api.EnsemblRestApiClient()

    class MockResponse:
        def __init__(self):
            self.status = 500

    mockresp = MockResponse()

    # Then it should trigger an exception
    with pytest.raises(Exception):
        result = client.except_on_invalid_response(mockresp)


def test_ping_ensemble_37():
    """Test ping ensembl server containing human build 37"""
    client = ensembl_api.EnsemblRestApiClient()
    data = client.ping_server()
    assert data == {"ping": 1}


def test_ping_ensemble_38():
    """Test ping ensembl server containing human build 38"""
    client = ensembl_api.EnsemblRestApiClient(build="38")
    data = client.ping_server()
    assert data == {"ping": 1}


def test_send_gene_request():
    """Test send request with correct params and endpoint"""
    url = "https://grch37.rest.ensembl.org/lookup/id/ENSG00000103591"
    client = ensembl_api.EnsemblRestApiClient()
    data = client.send_request(url)
    # get info for the ensembl gene
    assert data["display_name"] == "AAGAB"


def test_send_request_wrong_url():
    """Successful requests are tested by other tests in this file.
    This test will trigger errors instead.
    """
    not_an_url = "foo"
    client = ensembl_api.EnsemblRestApiClient()
    data = client.send_request(not_an_url)
    assert type(data) == MissingSchema

    url = f"https://grch37.rest.ensembl.org/{not_an_url}"
    data = client.send_request(url)
    assert type(data) == ValueError
