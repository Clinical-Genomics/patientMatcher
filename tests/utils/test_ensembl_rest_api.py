# -*- coding: UTF-8 -*-
import pytest
import responses
from patientMatcher.utils import ensembl_rest_client as ensembl_api
from requests.exceptions import MissingSchema


@responses.activate
def test_except_on_invalid_response():
    """Test function that creates exception with message when response returned from Ensembl REST API has status code !=200"""

    # GIVEN a response from Ensembl service with status != 200
    responses.add(
        responses.GET,
        f"https://rest.ensembl.org//info/ping",
        json={"ping": 1},
        status=500,
    )
    client = ensembl_api.EnsemblRestApiClient()

    # Then it should trigger an exception
    with pytest.raises(Exception):
        result = client.except_on_invalid_response(mockresp)


@responses.activate
def test_ping_ensembl():
    """Test ping ensembl server"""

    # GIVEN a mocked Ensembl REST API server
    responses.add(
        responses.GET,
        f"https://rest.ensembl.org//info/ping",
        json={"ping": 1},
        status=200,
    )

    client = ensembl_api.EnsemblRestApiClient(build="38")
    data = client.ping_server()
    assert data == {"ping": 1}


@responses.activate
def test_send_gene_request():
    """Test send request with correct params and endpoint"""

    # GIVEN a gene with Ensembl ID
    url = "https://grch37.rest.ensembl.org/lookup/id/ENSG00000103591"

    # GIVEN a mocked Ensembl gene lookup service:
    responses.add(
        responses.GET,
        url,
        json={"display_name": "AAGAB"},
        status=200,
    )

    client = ensembl_api.EnsemblRestApiClient()
    data = client.send_request(url)

    # get info for the ensembl gene
    assert data["display_name"] == "AAGAB"


@responses.activate
def test_send_request_wrong_url():
    """Successful requests are tested by other tests in this file.
    This test will trigger errors instead.
    """

    not_an_url = "foo"

    client = ensembl_api.EnsemblRestApiClient()
    data = client.send_request(not_an_url)
    assert type(data) == MissingSchema

    url = f"https://grch37.rest.ensembl.org/{not_an_url}"
    # GIVEN a mocked Ensembl gene lookup service:
    responses.add(
        responses.GET,
        url,
        json={"error": "page not found"},
        status=404,
    )
    data = client.send_request(url)
    assert type(data) == ValueError
